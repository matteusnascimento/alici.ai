#!/usr/bin/env python
"""
Integration test — Valida o fluxo completo de avatar upload
"""

from io import BytesIO

def test_avatar_upload_integration(client, auth_headers):
    """Test completo do fluxo de avatar upload"""
    
    # Step 1: Get profile (baseline)
    print("Step 1: Getting initial profile...")
    profile_resp = client.get("/api/account/profile", headers=auth_headers)
    assert profile_resp.status_code == 200
    initial_avatar = profile_resp.json().get("avatar_url")
    print(f"✅ Initial avatar: {initial_avatar or 'None'}")
    
    # Step 2: Upload valid avatar (PNG)
    print("\nStep 2: Uploading valid PNG avatar...")
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00'
        b'\x00\x01\x01\x00\x05\x18\r\n\x1b\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    upload_resp = client.post(
        "/api/account/upload-avatar",
        headers=auth_headers,
        files={"file": ("test.png", BytesIO(png_data), "image/png")}
    )
    assert upload_resp.status_code == 200, f"Upload failed: {upload_resp.text}"
    avatar_url = upload_resp.json()["avatar_url"]
    assert avatar_url.startswith("/uploads/avatars/"), f"Invalid URL: {avatar_url}"
    print(f"✅ Avatar uploaded: {avatar_url}")
    
    # Step 3: Try invalid file type
    print("\nStep 3: Testing invalid file rejection...")
    invalid_resp = client.post(
        "/api/account/upload-avatar",
        headers=auth_headers,
        files={"file": ("test.pdf", BytesIO(b"PDF content"), "application/pdf")}
    )
    assert invalid_resp.status_code == 400, f"Should reject PDF, got {invalid_resp.status_code}"
    assert "permitido" in invalid_resp.json()["detail"].lower()
    print(f"✅ Invalid file correctly rejected")
    
    # Step 4: Test file size limit
    print("\nStep 4: Testing file size limit...")
    large_data = b"x" * (6 * 1024 * 1024)  # 6MB
    size_resp = client.post(
        "/api/account/upload-avatar",
        headers=auth_headers,
        files={"file": ("large.png", BytesIO(large_data), "image/png")}
    )
    assert size_resp.status_code == 400, f"Should reject large file, got {size_resp.status_code}"
    assert "grande" in size_resp.json()["detail"].lower() or "5MB" in size_resp.json()["detail"]
    print(f"✅ Large file correctly rejected")
    
    print("\n" + "="*60)
    print("✅ ALL INTEGRATION TESTS PASSED")
    print("="*60)

if __name__ == "__main__":
    pass  # Use pytest to run
