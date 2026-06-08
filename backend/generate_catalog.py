"""Generate ~100 extra realistic products to simulate catalog scale.

The 20 hand-crafted products in data/products.json are the demo "hero" items
(and what the evals check). This script programmatically creates ~100 more
across more categories so the catalog feels real. seed_db.py inserts both.

A nice talking point: "I wrote a catalog generator to simulate scale and stress
the retrieval pipeline beyond the hero set."
"""
import random

random.seed(42)  # deterministic — same catalog every run

COLORS = {
    "Black": "أسود", "White": "أبيض", "Grey": "رمادي", "Navy": "كحلي",
    "Pink": "وردي", "Blue": "أزرق", "Beige": "بيج", "Green": "أخضر",
    "Mint": "نعناعي", "Sand": "رملي",
}

# category -> config. `slug` matches an SVG in frontend/public/images/.
CATEGORIES = {
    "Car Seats": {
        "code": "CS", "slug": "car-seats", "cat_ar": "مقاعد السيارة",
        "count": 8, "price": (180, 1900), "gift": True, "warn": False,
        "brands": {"Chicco": "شيكو", "Cybex": "سايبكس", "Joie": "جوي", "Graco": "جراكو", "Moon": "مون"},
        "types": [("Convertible Car Seat", "مقعد سيارة قابل للتحويل"), ("Infant Car Seat", "مقعد سيارة للرضّع"), ("Booster Seat", "مقعد داعم")],
        "age": ("Suitable from birth up to 12 years", "مناسب من الولادة حتى 12 عامًا"),
        "tags": ["car-seat", "isofix", "safety", "travel"], "color": True,
        "desc_en": "A safe, certified car seat with side-impact protection and a secure harness.",
        "desc_ar": "مقعد سيارة آمن ومعتمد مع حماية من الصدمات الجانبية وحزام تثبيت آمن.",
    },
    "Strollers": {
        "code": "ST", "slug": "strollers", "cat_ar": "عربات الأطفال",
        "count": 8, "price": (150, 1600), "gift": True, "warn": False,
        "brands": {"Cybex": "سايبكس", "Chicco": "شيكو", "Joie": "جوي", "Mamas & Papas": "ماماز آند باباز", "Teknum": "تكنوم"},
        "types": [("Lightweight Stroller", "عربة أطفال خفيفة"), ("Travel System", "نظام سفر"), ("Twin Stroller", "عربة توأم")],
        "age": ("Suitable from birth up to 4 years", "مناسبة من الولادة حتى 4 سنوات"),
        "tags": ["stroller", "travel", "lightweight"], "color": True,
        "desc_en": "A comfortable stroller with a smooth fold, large canopy, and a five-point harness.",
        "desc_ar": "عربة أطفال مريحة بطيّ سلس ومظلّة كبيرة وحزام أمان بخمس نقاط.",
    },
    "Baby Formula": {
        "code": "BF", "slug": "baby-formula", "cat_ar": "حليب الأطفال",
        "count": 8, "price": (32, 130), "gift": False, "warn": True,
        "brands": {"Aptamil": "أبتاميل", "Bebelac": "بيبيلاك", "Similac": "سيميلاك", "S26": "إس 26", "Pigeon": "بيجن"},
        "types": [("Stage 1 Infant Formula", "حليب أطفال المرحلة 1"), ("Stage 2 Follow-On", "حليب متابعة المرحلة 2"), ("Stage 3 Toddler Milk", "حليب المرحلة 3 للأطفال الصغار")],
        "age": ("Suitable for 0-12 months", "مناسب لعمر 0-12 شهرًا"),
        "tags": ["formula", "feeding", "milk"], "color": False, "size": ["400g", "800g", "900g"],
        "desc_en": "An infant milk formula with a nutrient blend to support healthy development.",
        "desc_ar": "حليب أطفال مع مزيج من العناصر الغذائية لدعم النمو الصحي.",
    },
    "Baby Monitors": {
        "code": "BM", "slug": "baby-monitors", "cat_ar": "أجهزة مراقبة الطفل",
        "count": 6, "price": (120, 800), "gift": True, "warn": False,
        "brands": {"Moon": "مون", "Teknum": "تكنوم", "Cybex": "سايبكس", "Motorola": "موتورولا"},
        "types": [("Video Baby Monitor", "جهاز مراقبة بالفيديو"), ("Audio Baby Monitor", "جهاز مراقبة صوتي"), ("Smart WiFi Monitor", "جهاز مراقبة ذكي بالواي فاي")],
        "age": ("Suitable for all ages", "مناسب لجميع الأعمار"),
        "tags": ["monitor", "safety", "nursery"], "color": True,
        "desc_en": "A baby monitor with clear night vision, two-way talk, and a temperature alert.",
        "desc_ar": "جهاز مراقبة للطفل مع رؤية ليلية واضحة ومحادثة ثنائية وتنبيه لدرجة الحرارة.",
    },
    "Gift Sets": {
        "code": "GS", "slug": "gift-sets", "cat_ar": "أطقم الهدايا",
        "count": 8, "price": (40, 500), "gift": True, "warn": False,
        "brands": {"Moon": "مون", "Chicco": "شيكو", "Jikel": "جيكل", "Mothercare": "مذركير"},
        "types": [("Newborn Gift Box", "صندوق هدايا للمولود"), ("Baby Shower Bundle", "حزمة استقبال مولود"), ("Bath Time Gift Set", "طقم هدايا الاستحمام")],
        "age": ("Suitable for 0-12 months", "مناسب لعمر 0-12 شهرًا"),
        "tags": ["gift", "gift-set", "baby-shower"], "color": True,
        "desc_en": "A thoughtfully curated gift set, beautifully presented — a popular baby-shower choice.",
        "desc_ar": "طقم هدايا منسّق بعناية ومعروض بشكل جميل — خيار شائع لحفلات استقبال المولود.",
    },
    "Feeding & Nursing": {
        "code": "FN", "slug": "feeding", "cat_ar": "التغذية والرضاعة",
        "count": 12, "price": (15, 600), "gift": True, "warn": False,
        "brands": {"Philips Avent": "فيليبس أفنت", "Tommee Tippee": "تومي تيبي", "Dr. Brown's": "دكتور براونز", "Pigeon": "بيجن", "Munchkin": "مانشكين"},
        "types": [("Anti-Colic Bottle Set", "طقم زجاجات مضادة للمغص"), ("Electric Breast Pump", "مضخة ثدي كهربائية"), ("Bottle Steriliser", "جهاز تعقيم زجاجات"), ("Bottle Warmer", "سخّان زجاجات"), ("Silicone Bib Set", "طقم مرايل سيليكون")],
        "age": ("Suitable from birth", "مناسب من الولادة"),
        "tags": ["feeding", "nursing", "bottle"], "color": True,
        "desc_en": "Practical feeding gear designed to make bottle-feeding easier and more hygienic.",
        "desc_ar": "أدوات تغذية عملية مصمّمة لجعل الرضاعة بالزجاجة أسهل وأكثر نظافة.",
    },
    "Diapering": {
        "code": "DP", "slug": "diapering", "cat_ar": "الحفّاضات",
        "count": 10, "price": (12, 160), "gift": False, "warn": False,
        "brands": {"Pampers": "بامبرز", "Huggies": "هاجيز", "MamyPoko": "مامي بوكو", "Molfix": "مولفيكس"},
        "types": [("Diapers Jumbo Pack", "حفّاضات عبوة كبيرة"), ("Pants-Style Diapers", "حفّاضات بنطال"), ("Sensitive Baby Wipes", "مناديل مبللة للبشرة الحسّاسة"), ("Newborn Diapers", "حفّاضات للمواليد")],
        "age": ("Newborn to toddler (sizes 1-6)", "من المواليد حتى الطفل الصغير (مقاسات 1-6)"),
        "tags": ["diapers", "wipes", "daily"], "color": False, "size": ["Size 1", "Size 2", "Size 3", "Size 4", "Size 5"],
        "desc_en": "Soft, absorbent diapering essentials with leak protection for day and night.",
        "desc_ar": "مستلزمات حفّاضات ناعمة وماصّة مع حماية من التسرّب نهارًا وليلاً.",
    },
    "Bath & Skincare": {
        "code": "BT", "slug": "bath", "cat_ar": "الاستحمام والعناية بالبشرة",
        "count": 10, "price": (10, 250), "gift": True, "warn": False,
        "brands": {"Johnson's": "جونسون", "Mustela": "موستيلا", "Sebamed": "سيباميد", "Chicco": "شيكو"},
        "types": [("Gentle Baby Wash", "غسول لطيف للأطفال"), ("Moisturising Lotion", "لوشن مرطّب"), ("Baby Bath Tub", "حوض استحمام للأطفال"), ("Hooded Towel Set", "طقم منشفة بغطاء رأس"), ("Diaper Rash Cream", "كريم لطفح الحفّاض")],
        "age": ("Suitable from birth", "مناسب من الولادة"),
        "tags": ["bath", "skincare", "gentle"], "color": True,
        "desc_en": "Gentle, dermatologically tested bath and skincare made for delicate baby skin.",
        "desc_ar": "منتجات استحمام وعناية لطيفة ومختبرة جلديًا لبشرة الطفل الرقيقة.",
    },
    "Nursery & Furniture": {
        "code": "NS", "slug": "nursery", "cat_ar": "غرفة الطفل والأثاث",
        "count": 10, "price": (90, 2200), "gift": False, "warn": False,
        "brands": {"Mothercare": "مذركير", "Moon": "مون", "Mamas & Papas": "ماماز آند باباز", "Teknum": "تكنوم"},
        "types": [("Convertible Cot Bed", "سرير أطفال قابل للتحويل"), ("Bedside Crib", "سرير جانبي"), ("Baby Bedding Set", "طقم مفروشات للطفل"), ("Changing Table", "طاولة تغيير الحفّاض"), ("Nursing Rocking Chair", "كرسي هزّاز للإرضاع")],
        "age": ("Suitable from birth up to 3 years", "مناسب من الولادة حتى 3 سنوات"),
        "tags": ["nursery", "furniture", "sleep"], "color": True,
        "desc_en": "Sturdy, safety-tested nursery furniture to create a cosy space for your baby.",
        "desc_ar": "أثاث غرفة أطفال متين ومختبر للسلامة لإنشاء مساحة دافئة لطفلك.",
    },
    "Toys & Learning": {
        "code": "TY", "slug": "toys", "cat_ar": "الألعاب والتعلّم",
        "count": 10, "price": (15, 400), "gift": True, "warn": False,
        "brands": {"Fisher-Price": "فيشر برايس", "Chicco": "شيكو", "VTech": "في تك", "Bright Starts": "برايت ستارز"},
        "types": [("Activity Play Gym", "صالة ألعاب للطفل"), ("Soft Plush Toy", "لعبة قطيفة ناعمة"), ("Stacking Rings Set", "طقم حلقات تركيب"), ("Musical Learning Table", "طاولة تعلّم موسيقية"), ("Baby Walker", "مشّاية للطفل")],
        "age": ("Suitable for 6-36 months", "مناسب لعمر 6-36 شهرًا"),
        "tags": ["toys", "learning", "play"], "color": True,
        "desc_en": "Colourful, age-appropriate toys that support play, motor skills, and early learning.",
        "desc_ar": "ألعاب ملوّنة ومناسبة للعمر تدعم اللعب والمهارات الحركية والتعلّم المبكّر.",
    },
    "Maternity": {
        "code": "MT", "slug": "maternity", "cat_ar": "الأمومة",
        "count": 10, "price": (25, 350), "gift": True, "warn": False,
        "brands": {"Mamas & Papas": "ماماز آند باباز", "Medela": "ميديلا", "Mothercare": "مذركير", "Chicco": "شيكو"},
        "types": [("Nursing Pillow", "وسادة إرضاع"), ("Maternity Support Belt", "حزام دعم للحامل"), ("Nursing Bra Set", "طقم حمّالات للإرضاع"), ("Pregnancy Body Pillow", "وسادة جسم للحامل"), ("Nipple Cream", "كريم للحلمات")],
        "age": ("Maternity & nursing", "للأمومة والإرضاع"),
        "tags": ["maternity", "nursing", "pregnancy"], "color": True,
        "desc_en": "Comfort-focused maternity and nursing essentials for pregnancy and beyond.",
        "desc_ar": "مستلزمات أمومة وإرضاع تركّز على الراحة أثناء الحمل وبعده.",
    },
}

FORMULA_WARNING = ("Breastfeeding is best for babies. Always consult a pediatrician or "
                   "healthcare professional before choosing or changing infant formula.")


def generate() -> list[dict]:
    products: list[dict] = []
    for cfg in CATEGORIES.values():
        brands = list(cfg["brands"].items())
        for i in range(cfg["count"]):
            seq = 101 + i
            pid = f"MW-{cfg['code']}-{seq}"
            brand_en, brand_ar = random.choice(brands)
            type_en, type_ar = random.choice(cfg["types"])

            # variant: a colour (gear) or a size (consumables)
            if cfg.get("color"):
                v_en, v_ar = random.choice(list(COLORS.items()))
            elif cfg.get("size"):
                v_en = v_ar = random.choice(cfg["size"])
            else:
                v_en = v_ar = ""

            price = round(random.uniform(*cfg["price"]) / 5) * 5 + 9  # e.g. 149, 264
            on_sale = random.random() < 0.4
            sale = round(price * 0.88 / 5) * 5 + 9 if on_sale else price
            sale = min(sale, price)

            suffix_en = f" - {v_en}" if v_en else ""
            suffix_ar = f" - {v_ar}" if v_ar else ""

            products.append({
                "id": pid,
                "sku": f"GEN-{cfg['code']}-{1000 + seq}",
                "name_en": f"{brand_en} - {type_en}{suffix_en}",
                "name_ar": f"{brand_ar} - {type_ar}{suffix_ar}",
                "brand": brand_en,
                "category": [c for c, v in CATEGORIES.items() if v is cfg][0],
                "subcategory": type_en,
                "price_aed": float(price),
                "sale_price_aed": float(sale),
                "tabby_installment_aed": round(sale / 4, 2),
                "rating": round(random.uniform(3.8, 4.9), 1),
                "rating_count": random.randint(5, 400),
                "recommended_age": cfg["age"][0],
                "age_group": cfg["age"][0],
                "weight_range_kg": "N/A",
                "isofix": cfg["code"] == "CS" and random.random() < 0.7,
                "i_size_certified": cfg["code"] == "CS" and random.random() < 0.6,
                "rotation_360": False,
                "rear_facing": cfg["code"] == "CS",
                "forward_facing": cfg["code"] == "CS",
                "safety_features": [],
                "key_features": [type_en, brand_en],
                "made_in": random.choice(["UAE", "China", "Germany", "Italy", "Netherlands", "Turkey"]),
                "in_stock": random.random() < 0.92,
                "stock_count": random.randint(0, 60),
                "gifting_suitable": cfg["gift"],
                "image_url": f"/images/{cfg['slug']}.svg",
                "description_en": f"{cfg['desc_en']} ({type_en} by {brand_en}.)",
                "description_ar": f"{cfg['desc_ar']} ({type_ar} من {brand_ar}.)",
                "warnings": FORMULA_WARNING if cfg["warn"] else "",
                "tags": cfg["tags"],
            })
    return products


if __name__ == "__main__":
    items = generate()
    print(f"Generated {len(items)} products across {len(CATEGORIES)} categories.")
