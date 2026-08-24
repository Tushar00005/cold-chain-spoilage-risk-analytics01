const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, PageOrientation
} = require("docx");
const fs = require("fs");

const ACCENT = "1D9E75";
const DARK = "222222";
const GRAY = "666666";

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } });
}
function p(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    spacing: { after: 160 },
  });
}
function bullet(text) {
  return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 80 } });
}

function kpiCell(label, value) {
  return new TableCell({
    width: { size: 33, type: WidthType.PERCENTAGE },
    shading: { type: ShadingType.CLEAR, fill: "F1F5F3" },
    margins: { top: 150, bottom: 150, left: 150, right: 150 },
    children: [
      new Paragraph({ children: [new TextRun({ text: label, size: 18, color: GRAY })], spacing: { after: 60 } }),
      new Paragraph({ children: [new TextRun({ text: value, size: 30, bold: true, color: ACCENT })] }),
    ],
  });
}

function dataTable(headers, rows, widths) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((htext, i) => new TableCell({
      width: { size: widths[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: "1D9E75" },
      margins: { top: 80, bottom: 80, left: 100, right: 100 },
      children: [new Paragraph({ children: [new TextRun({ text: htext, bold: true, color: "FFFFFF", size: 18 })] })],
    })),
  });
  const bodyRows = rows.map((r, idx) => new TableRow({
    children: r.map((cell, i) => new TableCell({
      width: { size: widths[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: idx % 2 === 0 ? "FFFFFF" : "F7F7F5" },
      margins: { top: 70, bottom: 70, left: 100, right: 100 },
      children: [new Paragraph({ children: [new TextRun({ text: String(cell), size: 18 })] })],
    })),
  }));
  const totalWidth = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: widths,
    rows: [headerRow, ...bodyRows],
  });
}

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 } } },
    children: [
      new Paragraph({
        children: [new TextRun({ text: "Cold Chain Integrity & Spoilage Risk Analytics", bold: true, size: 40, color: DARK })],
        spacing: { after: 80 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Business Insights Report — Perishable Logistics Program", size: 24, color: GRAY })],
        spacing: { after: 60 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Data sources: Python/Pandas cleaning · MySQL analysis · Power BI dashboard", size: 18, italics: true, color: GRAY })],
        spacing: { after: 300 },
      }),

      h1("1. Executive Summary"),
      p("Across 1,500 shipments analyzed in 2024, cold-chain performance shows meaningful, quantifiable risk. Temperature compliance stands at 64.7%, on-time delivery among completed shipments is 18.5%, and 50.3% of all shipments fall into the High Risk or Critical Risk spoilage categories. The rule-based spoilage-risk model estimates total financial exposure of $1,439,268.81 from potential spoiled inventory across the year."),
      p("The data points to two compounding drivers of loss: temperature excursions during transit, and delivery delays that extend a product's time outside safe storage conditions. Shipments that are both delayed and temperature-excursed carry the highest average loss per shipment, and delayed shipments are roughly twice as likely to land in the High/Critical risk bands as on-time shipments."),

      new Table({
        width: { size: 9350, type: WidthType.DXA },
        columnWidths: [3116, 3117, 3117],
        rows: [
          new TableRow({ children: [kpiCell("Total shipments", "1,500"), kpiCell("Temp. compliance", "64.7%"), kpiCell("On-time delivery", "18.5%")] }),
          new TableRow({ children: [kpiCell("Spoilage risk (High+Critical)", "50.3%"), kpiCell("Est. financial loss", "$1.44M"), kpiCell("Avg. transit time", "92.4 hrs")] }),
        ],
      }),
      new Paragraph({ text: "", spacing: { after: 200 } }),

      h1("2. Which Suppliers Require Attention?"),
      p("Supplier-level analysis compares each supplier's temperature-violation rate against the fleet-wide average (35.3%). Six of ten suppliers exceed this benchmark. The top five suppliers by total estimated financial loss are:"),
      dataTable(
        ["Supplier", "Total loss", "Shipments"],
        [
          ["Prime Cut Meats Co", "$164,071", "145"],
          ["Meadow Fresh Supplies", "$158,459", "163"],
          ["Highland Dairy Group", "$158,074", "148"],
          ["Coastal Catch Exports", "$149,643", "157"],
          ["Sunrise Produce Ltd", "$148,266", "158"],
        ],
        [4000, 2700, 2650]
      ),
      new Paragraph({ text: "", spacing: { after: 160 } }),
      p("Recommendation: open a corrective-action review with Prime Cut Meats Co, Highland Dairy Group, and Coastal Catch Exports first — they combine above-average violation rates with the highest absolute financial exposure."),

      h1("3. Which Routes Have the Highest Cold-Chain Risk?"),
      p("Filtering to routes with at least 5 shipments and ranking by temperature-excursion rate surfaces a clear top tier of high-risk lanes:"),
      dataTable(
        ["Route", "Excursion rate", "Shipments", "Total loss"],
        [
          ["Mexico City -> Los Angeles", "48.8%", "43", "$38,749"],
          ["Miami -> Los Angeles", "47.6%", "42", "$52,095"],
          ["Rotterdam -> Dallas", "45.5%", "66", "$50,820"],
          ["Chicago -> Dallas", "44.9%", "49", "$40,258"],
          ["New York -> Vancouver", "42.3%", "52", "$42,648"],
        ],
        [4200, 2000, 1600, 1550]
      ),
      new Paragraph({ text: "", spacing: { after: 160 } }),
      p("These five long-haul, cross-border lanes account for a disproportionate share of excursions relative to their shipment volume, suggesting equipment or handoff issues at origin/destination transfer points rather than random variation."),

      h1("4. Which Products Contribute Most to Potential Losses?"),
      p("At the category level, Vegetables ($404,171), Dairy ($348,321), and Meat ($293,433) drive the largest shares of total estimated loss. At the individual product level:"),
      dataTable(
        ["Product", "Estimated loss"],
        [
          ["Cheddar Cheese", "$133,883"],
          ["Tuna Steaks", "$127,963"],
          ["Mushrooms", "$113,718"],
          ["Whole Milk 1L", "$108,139"],
          ["Broccoli", "$96,799"],
        ],
        [6700, 2650]
      ),
      new Paragraph({ text: "", spacing: { after: 160 } }),
      p("Dairy and Seafood items carry an additional built-in risk weighting in the scoring model (spoilage-sensitive categories), which is reflected in Cheddar Cheese and Tuna Steaks topping the product-level loss ranking despite moderate shipment volumes."),

      h1("5. How Much Loss Is Tied to Temperature Excursions?"),
      p("Shipments with a severe temperature excursion (5C+ beyond the required range) account for $543,681 of the $1,439,269 total estimated loss — 37.8% of all financial exposure comes from this single failure mode, even though severe excursions represent a minority of shipments."),

      h1("6. How Strongly Do Delays Contribute to Spoilage Risk?"),
      p("58.9% of delayed shipments fall into the High or Critical spoilage-risk category, compared with 29.5% of on-time shipments — delayed shipments are roughly 2.0x as likely to be high-risk. Shipments that were both delayed and experienced a temperature excursion account for 77.7% of total estimated financial loss ($1,118,114), confirming that delay is not just an efficiency issue but a direct spoilage-risk multiplier, especially once a delay exceeds 24 hours."),

      h1("7. Where Should Management Prioritize Corrective Action?"),
      bullet("Cold-chain equipment audit on the five highest-excursion routes (Section 3), starting with Mexico City -> Los Angeles and Rotterdam -> Dallas."),
      bullet("Supplier corrective-action reviews for Prime Cut Meats Co, Highland Dairy Group, and Coastal Catch Exports, whose violation rates exceed the fleet average alongside high absolute losses."),
      bullet("Transit-time buffers or expedited handling for Dairy and Seafood shipments, given their built-in spoilage sensitivity and outsized contribution to per-unit loss."),
      bullet("Delay-reduction initiatives targeting shipments already showing early delay signals, since delay is the strongest amplifier of spoilage risk once it crosses the 24-hour threshold."),
      bullet("Sensor/IoT quality review: a measurable share of raw temperature readings were physically implausible (sensor error) and had to be excluded from analysis — improving sensor reliability will improve the accuracy of every KPI in this report."),

      h1("8. Methodology Note"),
      p("All figures in this report are produced by a fully transparent, rule-based pipeline: Python/Pandas for cleaning and feature engineering, MySQL for aggregate business-question queries, and Power BI for interactive exploration. The spoilage-risk classification is a documented point-scoring system (see clean_data.py) based on temperature excursion severity, excursion duration relative to transit time, delivery delay severity, and product category sensitivity — no machine learning or predictive modeling was used, per project scope.", { size: 18, color: GRAY, italics: true }),
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("Business_Insights_Report.docx", buffer);
  console.log("Report written.");
});
