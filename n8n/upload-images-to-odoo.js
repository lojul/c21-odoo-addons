// Use pdf.co to render PDF pages as images and upload to Odoo
// Convert pages one at a time to handle PDF.co page count inconsistencies
const data = $json;
const config = data._config;
const odooResult = data.odooResult || {};

let imageUploadResults = [];
let pdfCoResult = { success: false, pagesConverted: 0 };

// Only proceed if listing was created/updated successfully
if (!odooResult.success || !odooResult.listingId) {
  return { json: { ...data, odooResult: { ...odooResult, imagesUploaded: 0, imagesFailed: 0, imageDetails: [], pdfCoError: "No listing ID" } } };
}

const uid = odooResult.uid;
const listingId = odooResult.listingId;

// URL-encode the blob path (but keep slashes)
const encodedPath = data.blobPath.split("/").map(p => encodeURIComponent(p)).join("/");
const pdfUrl = "https://" + config.AZURE_BLOB_ACCOUNT + ".blob.core.windows.net/" + config.AZURE_BLOB_CONTAINER + "/" + encodedPath + "?" + config.AZURE_BLOB_READ_SAS;

// Max pages to attempt (to avoid infinite loops and excessive API usage)
const maxPagesToTry = 10;

try {
  // Convert pages one at a time until we hit an error or reach max
  // PDF.co uses 0-based indexing: page 0 = first page
  for (let pageIndex = 0; pageIndex < maxPagesToTry; pageIndex++) {
    const pageNum = pageIndex + 1; // For display/naming (1-based)
    let pdfCoResponse;
    try {
      pdfCoResponse = await this.helpers.httpRequest({
        method: "POST",
        url: "https://api.pdf.co/v1/pdf/convert/to/png",
        headers: {
          "x-api-key": config.PDF_CO_API_KEY,
          "Content-Type": "application/json"
        },
        body: {
          url: pdfUrl,
          pages: String(pageIndex),  // 0-based for PDF.co
          async: false
        },
        json: true
      });
    } catch (httpErr) {
      // HTTP error (like 454) - check if it's end of PDF
      if (httpErr.message && (httpErr.message.includes("454") || httpErr.message.includes("out of range"))) {
        pdfCoResult.success = true;
        pdfCoResult.stoppedAtIndex = pageIndex;
        pdfCoResult.totalPages = pageIndex;  // Successfully converted 0 to pageIndex-1
        pdfCoResult.reason = "Reached end of PDF (converted " + pageIndex + " pages)";
        break;
      } else {
        pdfCoResult.error = httpErr.message;
        break;
      }
    }

    // Also check response body for errors
    if (pdfCoResponse && pdfCoResponse.error) {
      if (pdfCoResponse.message && pdfCoResponse.message.includes("out of range")) {
        pdfCoResult.success = true;
        pdfCoResult.stoppedAtIndex = pageIndex;
        pdfCoResult.totalPages = pageIndex;
        pdfCoResult.reason = "Reached end of PDF (converted " + pageIndex + " pages)";
        break;
      } else {
        pdfCoResult.error = pdfCoResponse.message || JSON.stringify(pdfCoResponse);
        break;
      }
    }

    // Get the image URL
    const imageUrls = pdfCoResponse.urls || [];
    if (imageUrls.length === 0) {
      pdfCoResult.error = "No image URL returned for page " + pageNum;
      break;
    }

    pdfCoResult.pagesConverted = pageNum;  // 1-based count

    // Download and upload to Odoo
    try {
      const imageResponse = await this.helpers.httpRequest({
        method: "GET",
        url: imageUrls[0],
        encoding: "arraybuffer",
        returnFullResponse: true
      });

      const base64Image = Buffer.from(imageResponse.body).toString("base64");

      const imageData = {
        property_id: listingId,
        name: "Page " + pageNum,
        image: base64Image,
        sequence: pageNum,
        is_cover: pageNum === 1
      };

      const createImageResponse = await this.helpers.httpRequest({
        method: "POST",
        url: config.ODOO_URL + "/jsonrpc",
        headers: { "Content-Type": "application/json" },
        body: {
          jsonrpc: "2.0",
          method: "call",
          params: {
            service: "object",
            method: "execute_kw",
            args: [config.ODOO_DB, uid, config.ODOO_API_KEY, "c21.property.image", "create", [imageData]]
          },
          id: 20 + pageNum
        },
        json: true
      });

      if (createImageResponse.result) {
        imageUploadResults.push({ page: pageNum, success: true, imageId: createImageResponse.result });
      } else {
        imageUploadResults.push({ page: pageNum, success: false, error: createImageResponse.error || "Unknown Odoo error" });
      }
    } catch (imgErr) {
      imageUploadResults.push({ page: pageNum, success: false, error: imgErr.message });
    }
  }

  // Mark as success if we converted at least one page
  if (pdfCoResult.pagesConverted > 0) {
    pdfCoResult.success = true;
  }

} catch (e) {
  pdfCoResult.error = e.message;
}

// Summary
const successCount = imageUploadResults.filter(r => r.success).length;
const failCount = imageUploadResults.filter(r => !r.success).length;

return {
  json: {
    fileName: data.fileName,
    blobPath: data.blobPath,
    stats: data.stats,
    propertyData: data.propertyData,
    chunksIndexed: data.chunksIndexed,
    indexResult: data.indexResult,
    odooResult: {
      ...odooResult,
      pdfCoResult: pdfCoResult,
      imagesUploaded: successCount,
      imagesFailed: failCount,
      imageDetails: imageUploadResults
    }
  }
};
