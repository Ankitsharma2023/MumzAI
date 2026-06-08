"use client";

import { useState } from "react";
import { Product } from "@/lib/api";
import { Lang, STRINGS } from "@/lib/i18n";
import { realImage, mumzworldSearchUrl } from "@/lib/images";

export default function ProductCard({ p, lang }: { p: Product; lang: Lang }) {
  const t = STRINGS[lang];
  const [showReviews, setShowReviews] = useState(false);

  const name = lang === "ar" ? p.name_ar : p.name_en;
  const onSale = p.sale_price_aed && p.sale_price_aed < p.price_aed;
  const img = realImage(p.category, p.id) || p.image_url;
  const href = mumzworldSearchUrl(p);
  const reviews = p.reviews ?? [];

  function openReviews(e: React.MouseEvent) {
    e.preventDefault(); // don't follow the card's Mumzworld link
    e.stopPropagation();
    setShowReviews(true);
  }

  return (
    <>
      <a className="card" href={href} target="_blank" rel="noopener noreferrer">
        <img
          src={img}
          alt={name}
          loading="lazy"
          onError={(e) => {
            const el = e.currentTarget as HTMLImageElement;
            el.onerror = null;
            el.src = p.image_url;
          }}
        />
        <div className="card-body">
          <div className="card-brand">{p.brand}</div>
          <div className="card-name">{name}</div>

          <div className="price-row">
            <span className="price">AED {p.sale_price_aed || p.price_aed}</span>
            {onSale && <span className="price-was">AED {p.price_aed}</span>}
          </div>
          <div className="tabby">{t.tabby(p.tabby_installment_aed)}</div>

          {/* Review icon — opens the reviews modal */}
          <button type="button" className="rating-btn" onClick={openReviews} title={t.reviewsTitle}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M4 4h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H8l-4 4V6a2 2 0 0 1 2-2z" />
            </svg>
            <span>★ {p.rating}</span>
            <span className="rating-count">({p.rating_count} {t.reviews})</span>
          </button>

          <div className="chips">
            <span className="chip">{p.recommended_age}</span>
            {p.isofix && <span className="chip chip-isofix">ISOFIX</span>}
            <span className={"chip " + (p.in_stock ? "chip-stock" : "chip-oos")}>
              {p.in_stock ? t.inStock : t.outOfStock}
            </span>
          </div>

          <button type="button" className="feedback-link" onClick={openReviews}>
            {t.viewFeedback}
          </button>
          <div className="card-link">{t.viewOnMumzworld}</div>
        </div>
      </a>

      {showReviews && (
        <div className="modal-backdrop" onClick={() => setShowReviews(false)}>
          <div
            className="modal"
            dir={lang === "ar" ? "rtl" : "ltr"}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-head">
              <div>
                <div className="modal-eyebrow">{t.reviewsTitle}</div>
                <div className="modal-title">{name}</div>
              </div>
              <button
                type="button"
                className="modal-close"
                onClick={() => setShowReviews(false)}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className="modal-rating">★ {p.rating} · {p.rating_count} {t.reviews}</div>

            <div className="modal-reviews">
              {reviews.length > 0 ? (
                reviews.map((r, i) => (
                  <div key={i} className="review-item">
                    <div className="review-head">
                      <span className="review-author">{r.author}</span>
                      <span className="review-stars">
                        {"★".repeat(r.stars) + "☆".repeat(5 - r.stars)}
                      </span>
                    </div>
                    <div className="review-text">“{r.text}”</div>
                  </div>
                ))
              ) : (
                <div className="review-empty">{t.noReviews}</div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
