const data = $json;
const config = data._config;
const prop = data.propertyData || {};
const now = new Date();

const validDistricts = [
  "central", "admiralty", "wan_chai", "causeway_bay", "north_point",
  "quarry_bay", "taikoo", "wong_chuk_hang", "sheung_wan", "tsim_sha_tsui",
  "jordan", "mong_kok", "kowloon_bay", "kwun_tong", "san_po_kong",
  "kwai_chung", "tsuen_wan", "sha_tin", "fo_tan", "tuen_mun", "yuen_long", "other"
];
const district = validDistricts.includes(prop.district) ? prop.district : "other";
const listingType = prop.listing_type === "coworking" ? "coworking" : "leasing";
const validGrades = ["grade_a", "grade_b", "grade_c"];
const buildingGrade = validGrades.includes(prop.building_grade) ? prop.building_grade : null;

let descEn = "<div>";
if (prop.gross_area) descEn += "<p><strong>Gross Area:</strong> " + prop.gross_area + " sq.ft.</p>";
if (prop.net_area) descEn += "<p><strong>Net Area:</strong> " + prop.net_area + " sq.ft.</p>";
if (prop.asking_rent_text) descEn += "<p><strong>Asking Rent:</strong> " + prop.asking_rent_text + "</p>";
if (prop.service_charge_text) descEn += "<p><strong>Service Charge:</strong> " + prop.service_charge_text + "</p>";
if (prop.lease_terms) descEn += "<p><strong>Lease Terms:</strong> " + prop.lease_terms + "</p>";
if (prop.available_from_text) descEn += "<p><strong>Availability:</strong> " + prop.available_from_text + "</p>";
if (prop.handover_condition) descEn += "<p><strong>Handover:</strong> " + prop.handover_condition + "</p>";
if (prop.description_en) descEn += "<p>" + prop.description_en + "</p>";
descEn += "<hr/><p><small>Source: " + data.fileName + " | Processed: " + now.toISOString() + "</small></p></div>";

let descCn = "<div>";
if (prop.gross_area) descCn += "<p><strong>建築面積:</strong> " + prop.gross_area + " 平方尺</p>";
if (prop.net_area) descCn += "<p><strong>實用面積:</strong> " + prop.net_area + " 平方尺</p>";
if (prop.asking_rent_text) descCn += "<p><strong>租金:</strong> " + prop.asking_rent_text + "</p>";
if (prop.service_charge_text) descCn += "<p><strong>管理費:</strong> " + prop.service_charge_text + "</p>";
if (prop.lease_terms) descCn += "<p><strong>租約條款:</strong> " + prop.lease_terms + "</p>";
if (prop.available_from_text) descCn += "<p><strong>可租日期:</strong> " + prop.available_from_text + "</p>";
if (prop.description_cn) descCn += "<p>" + prop.description_cn + "</p>";
descCn += "</div>";

let odooResult = { success: false };

try {
  const authResponse = await this.helpers.httpRequest({
    method: "POST",
    url: config.ODOO_URL + "/jsonrpc",
    headers: { "Content-Type": "application/json" },
    body: {
      jsonrpc: "2.0",
      method: "call",
      params: {
        service: "common",
        method: "authenticate",
        args: [config.ODOO_DB, config.ODOO_USERNAME, config.ODOO_API_KEY, {}]
      },
      id: 1
    },
    json: true
  });
  const uid = authResponse.result;
  if (!uid) throw new Error("Odoo auth failed");

  let propertyTypeId = null;
  if (prop.property_type) {
    const ptResponse = await this.helpers.httpRequest({
      method: "POST",
      url: config.ODOO_URL + "/jsonrpc",
      headers: { "Content-Type": "application/json" },
      body: {
        jsonrpc: "2.0",
        method: "call",
        params: {
          service: "object",
          method: "execute_kw",
          args: [
            config.ODOO_DB, uid, config.ODOO_API_KEY,
            "c21.property.type", "search",
            [[["code", "=", prop.property_type]]],
            { limit: 1 }
          ]
        },
        id: 10
      },
      json: true
    });
    if (ptResponse.result && ptResponse.result.length > 0) {
      propertyTypeId = ptResponse.result[0];
    }
  }

  let businessTypeIds = [];
  if (prop.business_type) {
    const btResponse = await this.helpers.httpRequest({
      method: "POST",
      url: config.ODOO_URL + "/jsonrpc",
      headers: { "Content-Type": "application/json" },
      body: {
        jsonrpc: "2.0",
        method: "call",
        params: {
          service: "object",
          method: "execute_kw",
          args: [
            config.ODOO_DB, uid, config.ODOO_API_KEY,
            "c21.business.type", "search",
            [[["code", "=", prop.business_type]]],
            { limit: 1 }
          ]
        },
        id: 11
      },
      json: true
    });
    if (btResponse.result && btResponse.result.length > 0) {
      businessTypeIds = btResponse.result;
    }
  }

  const searchResponse = await this.helpers.httpRequest({
    method: "POST",
    url: config.ODOO_URL + "/jsonrpc",
    headers: { "Content-Type": "application/json" },
    body: {
      jsonrpc: "2.0",
      method: "call",
      params: {
        service: "object",
        method: "execute_kw",
        args: [
          config.ODOO_DB, uid, config.ODOO_API_KEY,
          "c21.property.listing", "search",
          [[["description", "ilike", "Source: " + data.fileName]]],
          { limit: 1 }
        ]
      },
      id: 2
    },
    json: true
  });

  const existingIds = searchResponse.result || [];
  const existingId = existingIds.length > 0 ? existingIds[0] : null;

  const listingData = {
    name: prop.name || data.fileName.replace(/\.pdf$/i, "").replace(/_/g, " "),
    listing_type: listingType,
    district: district,
    description: descEn,
    description_cn: descCn
  };

  if (prop.name_cn) listingData.name_cn = prop.name_cn;
  if (prop.building_name) listingData.building_name = prop.building_name;
  if (prop.address) listingData.address = prop.address;
  if (prop.floor) listingData.floor = prop.floor;
  if (prop.unit) listingData.unit = prop.unit;
  if (propertyTypeId) listingData.property_type_id = propertyTypeId;
  if (buildingGrade) listingData.building_grade = buildingGrade;
  if (businessTypeIds.length > 0) listingData.business_type_ids = [[6, 0, businessTypeIds]];
  if (prop.gross_area && !isNaN(Number(prop.gross_area))) listingData.gross_area = Number(prop.gross_area);
  if (prop.net_area && !isNaN(Number(prop.net_area))) listingData.net_area = Number(prop.net_area);
  if (prop.asking_rent && !isNaN(Number(prop.asking_rent))) listingData.asking_rent = Number(prop.asking_rent);
  if (prop.rent_per_sqft && !isNaN(Number(prop.rent_per_sqft))) listingData.rent_per_sqft = Number(prop.rent_per_sqft);
  if (prop.lease_terms) listingData.lease_terms = prop.lease_terms;
  if (prop.available_from && /^\d{4}-\d{2}-\d{2}$/.test(prop.available_from)) listingData.available_from = prop.available_from;

  let listingId, refCode, isUpdate = false;

  if (existingId) {
    isUpdate = true;
    listingId = existingId;

    const readResponse = await this.helpers.httpRequest({
      method: "POST",
      url: config.ODOO_URL + "/jsonrpc",
      headers: { "Content-Type": "application/json" },
      body: {
        jsonrpc: "2.0",
        method: "call",
        params: {
          service: "object",
          method: "execute_kw",
          args: [
            config.ODOO_DB, uid, config.ODOO_API_KEY,
            "c21.property.listing", "read",
            [[existingId], ["ref_code"]]
          ]
        },
        id: 3
      },
      json: true
    });
    refCode = (readResponse.result && readResponse.result[0]) ? readResponse.result[0].ref_code : "PROP-" + Date.now().toString(36).toUpperCase();

    await this.helpers.httpRequest({
      method: "POST",
      url: config.ODOO_URL + "/jsonrpc",
      headers: { "Content-Type": "application/json" },
      body: {
        jsonrpc: "2.0",
        method: "call",
        params: {
          service: "object",
          method: "execute_kw",
          args: [
            config.ODOO_DB, uid, config.ODOO_API_KEY,
            "c21.property.listing", "write",
            [[existingId], listingData]
          ]
        },
        id: 4
      },
      json: true
    });

    const existingImagesResponse = await this.helpers.httpRequest({
      method: "POST",
      url: config.ODOO_URL + "/jsonrpc",
      headers: { "Content-Type": "application/json" },
      body: {
        jsonrpc: "2.0",
        method: "call",
        params: {
          service: "object",
          method: "execute_kw",
          args: [
            config.ODOO_DB, uid, config.ODOO_API_KEY,
            "c21.property.image", "search",
            [[["property_id", "=", existingId]]]
          ]
        },
        id: 5
      },
      json: true
    });
    const existingImageIds = existingImagesResponse.result || [];

    if (existingImageIds.length > 0) {
      await this.helpers.httpRequest({
        method: "POST",
        url: config.ODOO_URL + "/jsonrpc",
        headers: { "Content-Type": "application/json" },
        body: {
          jsonrpc: "2.0",
          method: "call",
          params: {
            service: "object",
            method: "execute_kw",
            args: [
              config.ODOO_DB, uid, config.ODOO_API_KEY,
              "c21.property.image", "unlink",
              [existingImageIds]
            ]
          },
          id: 6
        },
        json: true
      });
    }

    odooResult = {
      success: true,
      listingId: listingId,
      uid: uid,
      refCode: refCode,
      isUpdate: true,
      deletedImages: existingImageIds.length,
      propertyTypeId: propertyTypeId,
      businessTypeIds: businessTypeIds,
      data: listingData
    };

  } else {
    refCode = "PROP-" + now.getFullYear() + String(now.getMonth() + 1).padStart(2, "0") + String(now.getDate()).padStart(2, "0") + "-" + Date.now().toString(36).toUpperCase();
    listingData.ref_code = refCode;
    listingData.approval_status = "draft";
    listingData.state = "available";

    const createResponse = await this.helpers.httpRequest({
      method: "POST",
      url: config.ODOO_URL + "/jsonrpc",
      headers: { "Content-Type": "application/json" },
      body: {
        jsonrpc: "2.0",
        method: "call",
        params: {
          service: "object",
          method: "execute_kw",
          args: [
            config.ODOO_DB, uid, config.ODOO_API_KEY,
            "c21.property.listing", "create",
            [listingData]
          ]
        },
        id: 7
      },
      json: true
    });

    if (createResponse.result) {
      listingId = createResponse.result;
      odooResult = {
        success: true,
        listingId: listingId,
        uid: uid,
        refCode: refCode,
        isUpdate: false,
        propertyTypeId: propertyTypeId,
        businessTypeIds: businessTypeIds,
        data: listingData
      };
    } else {
      odooResult = {
        success: false,
        error: createResponse.error || "Unknown error",
        data: listingData
      };
    }
  }

} catch (e) {
  odooResult = { success: false, error: e.message };
}

return {
  json: {
    fileName: data.fileName,
    blobPath: data.blobPath,
    stats: data.stats,
    propertyData: data.propertyData,
    extractedImages: data.extractedImages,
    chunksIndexed: data.chunksIndexed,
    imagesProcessed: data.imagesProcessed,
    indexResult: data.indexResult,
    odooResult: odooResult,
    _config: config
  }
};
