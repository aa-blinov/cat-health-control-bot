"""Tests for data export endpoints."""

import pytest
from datetime import datetime
import csv
import io


@pytest.mark.health
class TestDataExport:
    """Test data export endpoints."""
    
    def test_export_asthma_csv(self, client, mock_db, regular_user_token, test_pet):
        """Test exporting asthma attacks as CSV."""
        # Add some asthma attacks
        from web.app import db
        db["asthma_attacks"].insert_many([
            {
                "pet_id": str(test_pet["_id"]),
                "date_time": datetime(2024, 1, 15, 14, 30),
                "duration": "5 minutes",
                "reason": "Stress",
                "inhalation": True,
                "comment": "Attack 1"
            },
            {
                "pet_id": str(test_pet["_id"]),
                "date_time": datetime(2024, 1, 16, 10, 0),
                "duration": "3 minutes",
                "reason": "Exercise",
                "inhalation": False,
                "comment": "Attack 2"
            }
        ])
        
        response = client.get(
            f"/api/export/asthma/csv?pet_id={test_pet['_id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        assert response.status_code == 200
        assert response.content_type == "text/csv"
        assert "attachment" in response.headers.get("Content-Disposition", "")
        
        # Verify CSV content
        content = response.data.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) == 3  # Header + 2 data rows
        assert "Дата и время" in rows[0]
    
    def test_export_defecation_tsv(self, client, mock_db, regular_user_token, test_pet):
        """Test exporting defecations as TSV."""
        from web.app import db
        db["defecations"].insert_one({
            "pet_id": str(test_pet["_id"]),
            "date_time": datetime(2024, 1, 15, 14, 30),
            "stool_type": "Normal",
            "color": "Brown",
            "food": "Dry food",
            "comment": "Test"
        })
        
        response = client.get(
            f"/api/export/defecation/tsv?pet_id={test_pet['_id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        assert response.status_code == 200
        assert response.content_type == "text/tab-separated-values"
    
    def test_export_weight_html(self, client, mock_db, regular_user_token, test_pet):
        """Test exporting weights as HTML."""
        from web.app import db
        db["weights"].insert_one({
            "pet_id": str(test_pet["_id"]),
            "date_time": datetime(2024, 1, 15, 14, 30),
            "weight": "4.5",
            "food": "Dry food",
            "comment": "Test"
        })
        
        response = client.get(
            f"/api/export/weight/html?pet_id={test_pet['_id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        assert response.status_code == 200
        assert response.content_type == "text/html"
        assert b"<html" in response.data
        assert "Вес".encode("utf-8") in response.data
    
    def test_export_litter_markdown(self, client, mock_db, regular_user_token, test_pet):
        """Test exporting litter changes as Markdown."""
        from web.app import db
        db["litter_changes"].insert_one({
            "pet_id": str(test_pet["_id"]),
            "date_time": datetime(2024, 1, 15, 14, 30),
            "comment": "Test change"
        })
        
        response = client.get(
            f"/api/export/litter/md?pet_id={test_pet['_id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        assert response.status_code == 200
        assert response.content_type == "text/markdown"
        assert b"# " in response.data
        assert "Смена лотка".encode("utf-8") in response.data
    
    def test_export_feeding_csv(self, client, mock_db, regular_user_token, test_pet):
        """Test exporting feedings as CSV."""
        from web.app import db
        db["feedings"].insert_one({
            "pet_id": str(test_pet["_id"]),
            "date_time": datetime(2024, 1, 15, 8, 0),
            "food_weight": "100",
            "comment": "Morning feeding"
        })
        
        response = client.get(
            f"/api/export/feeding/csv?pet_id={test_pet['_id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        assert response.status_code == 200
        assert response.content_type == "text/csv"
    
    def test_export_requires_pet_id(self, client, regular_user_token):
        """Test that export requires pet_id."""
        response = client.get(
            "/api/export/asthma/csv",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_export_invalid_type(self, client, regular_user_token, test_pet):
        """Test export with invalid export type."""
        response = client.get(
            f"/api/export/invalid/csv?pet_id={test_pet['_id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_export_invalid_format(self, client, mock_db, regular_user_token, test_pet):
        """Test export with invalid format type."""
        # Add some data first
        from web.app import db
        db["asthma_attacks"].insert_one({
            "pet_id": str(test_pet["_id"]),
            "date_time": datetime(2024, 1, 15, 14, 30),
            "duration": "5 minutes",
            "reason": "Stress",
            "inhalation": True,
            "comment": "Test"
        })
        
        response = client.get(
            f"/api/export/asthma/invalid?pet_id={test_pet['_id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_export_no_data(self, client, mock_db, regular_user_token, test_pet):
        """Test export when no data exists."""
        response = client.get(
            f"/api/export/asthma/csv?pet_id={test_pet['_id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
    
    def test_export_no_access(self, client, mock_db, regular_user_token, admin_pet):
        """Test export without pet access."""
        response = client.get(
            f"/api/export/asthma/csv?pet_id={admin_pet['_id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert "error" in data
    
    def test_export_csv_encoding(self, client, mock_db, regular_user_token, test_pet):
        """Test CSV export has proper encoding (UTF-8 with BOM for Excel)."""
        from web.app import db
        db["asthma_attacks"].insert_one({
            "pet_id": str(test_pet["_id"]),
            "date_time": datetime(2024, 1, 15, 14, 30),
            "duration": "5 минут",
            "reason": "Стресс",
            "inhalation": True,
            "comment": "Тест"
        })
        
        response = client.get(
            f"/api/export/asthma/csv?pet_id={test_pet['_id']}",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        assert response.status_code == 200
        # Check for BOM (UTF-8 signature)
        assert response.data.startswith(b"\xef\xbb\xbf") or response.data.startswith(b"\xff\xfe")

