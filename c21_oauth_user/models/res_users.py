from odoo import models, api, fields
from odoo.exceptions import UserError, AccessDenied
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        """Override to auto-link existing users by email when oauth_uid is empty.

        When a user is created manually with OAuth Provider set but no OAuth UID,
        this will automatically link them on first SSO login by matching email.
        """
        oauth_uid = validation['user_id']
        email = validation.get('email')

        # First try normal lookup by oauth_uid + provider
        oauth_user = self.search([
            ("oauth_uid", "=", oauth_uid),
            ('oauth_provider_id', '=', provider)
        ])

        if not oauth_user and email:
            # Try to find user by email + provider where oauth_uid is empty
            oauth_user = self.search([
                ('login', '=', email),
                ('oauth_provider_id', '=', provider),
                ('oauth_uid', '=', False),
            ])
            if not oauth_user:
                # Also try matching by email field
                oauth_user = self.search([
                    ('email', '=', email),
                    ('oauth_provider_id', '=', provider),
                    ('oauth_uid', '=', False),
                ])

            if oauth_user:
                _logger.info(
                    "Auto-linking user %s to OAuth UID %s (matched by email)",
                    oauth_user.login, oauth_uid
                )
                # Update the oauth_uid for this user
                oauth_user.write({'oauth_uid': oauth_uid})

        if not oauth_user:
            # Fall back to parent behavior (will try to create user or raise AccessDenied)
            return super()._auth_oauth_signin(provider, validation, params)

        if len(oauth_user) > 1:
            raise AccessDenied("Multiple users found for OAuth credentials")

        oauth_user.write({'oauth_access_token': params['access_token']})
        return oauth_user.login

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-confirm SSO users and skip mail notifications.

        When a user is created with an OAuth provider set:
        1. Skip mail notifications/logging (prevents deadlock with mail module)
        2. Auto-confirm user (no invitation email needed)
        """
        # Check if any user has OAuth provider - if so, skip mail notifications
        has_oauth = any(vals.get('oauth_provider_id') for vals in vals_list)

        if has_oauth:
            # Add context to skip auth_signup's invitation email and mail module tracking
            # no_reset_password: prevents auth_signup from calling _action_reset_password
            # The other flags prevent mail module's message posting and tracking
            self = self.with_context(
                no_reset_password=True,  # Key flag to skip invitation email
                mail_create_nolog=True,
                mail_notrack=True,
                mail_create_nosubscribe=True,
                tracking_disable=True,
            )
            _logger.info("Creating user with OAuth provider - skipping invitation email")

        users = super(ResUsers, self).create(vals_list)

        # Auto-confirm users that have OAuth provider set
        for user in users:
            if user.oauth_provider_id:
                _logger.info(
                    "User %s has OAuth provider set - marked as confirmed (no invitation needed)",
                    user.login
                )
                # Clear any signup token to mark as confirmed (if auth_signup fields exist)
                if user.partner_id and hasattr(user.partner_id, 'signup_token'):
                    user.partner_id.sudo().with_context(
                        mail_create_nolog=True,
                        mail_notrack=True,
                    ).signup_cancel()

        return users

    def action_reset_password(self):
        """Override to skip password reset email for SSO users.

        SSO users don't need password reset emails - they login via OAuth.
        """
        # Filter out users with OAuth provider
        non_oauth_users = self.filtered(lambda u: not u.oauth_provider_id)
        oauth_users = self.filtered(lambda u: u.oauth_provider_id)

        if oauth_users:
            _logger.info(
                "Skipping password reset email for %d SSO user(s): %s",
                len(oauth_users),
                ', '.join(oauth_users.mapped('login'))
            )

        if non_oauth_users:
            return super(ResUsers, non_oauth_users).action_reset_password()

        # If all users are OAuth users, do nothing
        return True

    def unlink(self):
        """Override unlink to also delete orphaned partner records.

        When a user is deleted, their associated partner record often remains
        as an orphan, which can cause issues when recreating users with the
        same email. This override cleans up those partners.
        """
        # Collect partners that should be deleted with the users
        partners_to_delete = self.env['res.partner']

        for user in self:
            partner = user.partner_id
            if partner:
                # Check if this partner is ONLY used by this user
                # Don't delete if partner is used elsewhere (e.g., as a contact, customer)
                other_users = self.env['res.users'].sudo().search([
                    ('partner_id', '=', partner.id),
                    ('id', '!=', user.id)
                ])

                # Check if partner has any other references (invoices, sales orders, etc.)
                # For safety, only delete if partner was created specifically for this user
                # (i.e., partner type is 'contact' and has no child contacts)
                if not other_users and partner.type == 'contact':
                    has_children = self.env['res.partner'].sudo().search_count([
                        ('parent_id', '=', partner.id)
                    ])
                    if not has_children:
                        partners_to_delete |= partner
                        _logger.info(
                            "Partner %s (%s) will be deleted with user %s",
                            partner.id, partner.email, user.login
                        )

        # Delete the users first
        result = super().unlink()

        # Then delete the orphaned partners
        if partners_to_delete:
            _logger.info("Cleaning up %d orphaned partner(s)", len(partners_to_delete))
            partners_to_delete.sudo().unlink()

        return result
