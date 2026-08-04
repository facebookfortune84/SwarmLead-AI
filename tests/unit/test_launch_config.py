"""Unit tests for the launch campaign config (core.services.launch_config)."""

from core.services import launch_config


def test_status_exposes_launch_metadata():
    status = launch_config.status()
    assert status["launched"] is True
    assert "producthunt.com" in status["product_hunt_url"]
    assert status["promo"]["code"] == "LAUNCH100"
    assert status["referral"]["referrer_reward"] == "$50 credit"


def test_share_links_cover_all_networks():
    links = launch_config.share_links()
    assert set(links) == {"x", "facebook", "linkedin", "whatsapp", "email"}
    assert "twitter.com/intent/tweet" in links["x"]
    assert "facebook.com/sharer" in links["facebook"]
    assert "linkedin.com/sharing" in links["linkedin"]
    assert "wa.me" in links["whatsapp"]
    assert links["email"].startswith("mailto:")


def test_share_links_are_url_encoded():
    links = launch_config.share_links()
    # The target URL must appear URL-encoded, not raw (safe browser opening)
    assert "https://" not in links["x"].split("url=")[1].split("&")[0]


def test_compose_traffic_drafts_returns_social_and_ph():
    drafts = launch_config.compose_traffic_drafts()
    networks = {d["network"] for d in drafts}
    assert {"x", "linkedin", "facebook", "reddit", "product_hunt"} <= networks
    assert all(d.get("kind") in {"social_post", "ph_comment"} for d in drafts)
    assert all(d["text"] for d in drafts)


def test_social_posts_mention_product_hunt():
    texts = " ".join(p["text"] for p in launch_config.SOCIAL_POSTS)
    assert "producthunt.com" in texts


def test_is_launch_week_true_after_launch():
    # The launch constant is Aug 3 2026; tests run after that date.
    assert launch_config.is_launch_week() is True
