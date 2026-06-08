// Real Mumzworld product images (hot-linked from their CDN, verified loadable)
// assigned per category. Our generated products have made-up SKUs, so we can't
// map exact images — instead each card gets a real, category-appropriate photo.
// ProductCard falls back to the local placeholder SVG if any image fails to load.

const CDN = "https://s3-pwa-prod.mumzworld.com/media/catalog/product/";

const POOLS: Record<string, string[]> = {
  "Car Seats": [
    "TC-MNBGCBK01-1.jpg",
    "18179364-JK804448_95-1.png",
    "TC-MNNCSMT03-1.jpg",
  ],
  "Strollers": [
    "4/4/44483883-909-nbr121bk-1_1.jpg",
    "0/0/00-prime-3-sand-dune-5902533928958.jpg",
    "34156323-KSESME00BLK300N-1.jpg",
    "DK-SP150-20-033-034-1.jpg",
    "JRT-JK801116-99-1.jpg",
  ],
  "Baby Formula": [
    "2804452-92000010-1.png",
    "SEST-5060040253700-1.jpg",
    "AE-5016533651485-1.jpg",
    "AG-AA3000088-1.jpg",
  ],
  "Feeding & Nursing": [
    "SCY90302-1.jpg",
    "524-81231-1.jpg",
    "3483-SCY900-02-1.jpg",
    "TC-BRZ0103-1.jpg",
    "TC-FRP0046-1.jpg",
  ],
  "Diapering": [
    "SBF-LS_DCM_WH100-1.jpg",
    "ASTA-KC65303-1.jpg",
    "MCH-BBDB-W-1.jpg",
  ],
  "Bath & Skincare": [
    "4140193-MUS6290362580348-1.png",
    "38394224-QM2278S-1.jpg",
    "ASK-8702824-1.jpg",
    "ASK-8702842-1.jpg",
    "ASK-8702855-1.jpg",
  ],
  "Toys & Learning": [
    "30926520-SN097-1.jpg",
    "MMFC-X001TX23RD-1.jpg",
    "MD-303325-1.jpg",
  ],
  "Baby Monitors": [
    "38394224-QMBM016-1.jpg",
    "4/5/45032944-hb6052-1.jpg",
    "4/1/4107390-dm685-1.jpg",
    "38939729-N311SLB-1.jpg",
    "P/S/PS-VTBM2000.jpg",
  ],
  "Gift Sets": [
    "AWL-H002SY2004-A27B-1.jpg",
    "HRG-RT0050-1.jpg",
    "AWL-H002SY2004-A01-1.jpg",
  ],
  "Nursery & Furniture": [
    "SBF-TK_WBSC_WH-1.jpg",
    "SBF-TK_BSC_IV-1.jpg",
    "QING-BB_KB488-1.jpg",
    "JRT-JK808801-90-1.jpg",
    "18179364-JK808802-90-1.jpg",
  ],
  "Maternity": [
    "SCY90302-1.jpg",
    "524-81231-1.jpg",
    "3483-SCY900-02-1.jpg",
    "TC-BRZ0103-1.jpg",
    "TC-FRP0046-1.jpg",
  ],
};

function hash(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h;
}

// A real Mumzworld image for this product's category, or null (→ use placeholder).
export function realImage(category: string, id: string): string | null {
  const pool = POOLS[category];
  if (!pool || pool.length === 0) return null;
  return CDN + pool[hash(id) % pool.length];
}

// Deep-link the card to a Mumzworld search for this product.
export function mumzworldSearchUrl(p: {
  name_en: string;
  brand: string;
  subcategory?: string;
}): string {
  const q = `${p.brand} ${p.subcategory ?? ""}`.trim() || p.name_en;
  return `https://www.mumzworld.com/en/search?q=${encodeURIComponent(q)}`;
}
