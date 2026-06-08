"""Attach a list of plausible parent reviews to each product (deterministic per id).

Real Mumzworld products have many reviews; our dummy catalog doesn't, so we
generate ~7 representative ones (with reviewer name + star rating) so the reviews
modal has real content to scroll. The assistant only summarises these — never
invents reviews.
"""
import hashlib
import random

NAMES = [
    "Aisha M.", "Sara K.", "Fatima A.", "Layla H.", "Noura S.", "Mariam T.",
    "Huda R.", "Reem A.", "Priya S.", "Anita G.", "Emily R.", "Jessica P.",
    "Hala D.", "Maya N.", "Zoya I.", "Dana F.",
]

POSITIVE = [
    "Excellent quality — my baby loves it.",
    "Great value for the price, would buy again.",
    "Exactly as described and delivery was fast.",
    "Sturdy and well made, very happy with it.",
    "Easy to use and clean. Highly recommend.",
    "Perfect for my little one, five stars.",
    "Soft, safe, and good quality.",
    "Does exactly what it promises — no complaints.",
    "Bought it as a gift and the mom loved it.",
    "Better than I expected, great purchase.",
    "Looks premium and feels durable.",
    "My second one — that's how good it is.",
]
MILD = [
    "Good overall, but a little pricey.",
    "Does the job; packaging could be better.",
    "Decent quality, took a little getting used to.",
    "Works well, though smaller than I expected.",
    "Happy with it, delivery took a couple of days.",
    "It's fine — nothing special but reliable.",
]


def make_reviews(product: dict) -> list[dict]:
    rating = product.get("rating", 4.2)
    seed = int(hashlib.md5(product["id"].encode()).hexdigest(), 16)
    rnd = random.Random(seed)

    if rating >= 4.4:
        n_pos, n_mild = 6, 1
    elif rating >= 4.0:
        n_pos, n_mild = 5, 2
    else:
        n_pos, n_mild = 3, 4

    pos = rnd.sample(POSITIVE, min(n_pos, len(POSITIVE)))
    mild = rnd.sample(MILD, min(n_mild, len(MILD)))
    items = [(t, "pos") for t in pos] + [(t, "mild") for t in mild]
    rnd.shuffle(items)

    names = rnd.sample(NAMES, len(items))
    reviews = []
    for i, (text, kind) in enumerate(items):
        if kind == "pos":
            stars = 5 if rnd.random() < 0.7 else 4
        else:
            stars = rnd.choice([3, 4])
        reviews.append({"author": names[i], "stars": stars, "text": text})
    return reviews
