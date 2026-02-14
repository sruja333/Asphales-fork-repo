"""Tests for contextual URL/domain risk logic."""

from context_engine import calculate_contextual_risk


def test_safe_tld_com_not_flagged_by_domain_only():
    text = "Please check details at https://example.com/account"
    result = calculate_contextual_risk(text=text, detected_features=[], links=None, base_score=0.0)
    assert "Suspicious URL structure" not in result["detected_signals"]


def test_safe_tld_in_not_flagged_by_domain_only():
    text = "Track your parcel at https://postoffice.in/track"
    result = calculate_contextual_risk(text=text, detected_features=[], links=None, base_score=0.0)
    assert "Suspicious URL structure" not in result["detected_signals"]


def test_unknown_tld_flagged_as_suspicious():
    text = "Verify now at https://bank-alert.verify-login.ru/secure"
    result = calculate_contextual_risk(text=text, detected_features=[], links=None, base_score=0.0)
    assert "Suspicious URL structure" in result["detected_signals"]
    assert result["risk_score"] >= 0.1


def test_domain_signal_combined_with_credential_terms_boosts_risk():
    text = "Update KYC and OTP now at https://account-verify.alert-login.xyz"
    result = calculate_contextual_risk(text=text, detected_features=[], links=None, base_score=0.0)
    assert "Suspicious URL structure" in result["detected_signals"]
    assert result["risk_score"] >= 0.1
