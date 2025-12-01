import pytest
from unittest.mock import MagicMock, patch
from src.services.meeting_tool_service.meeting_tool_service import process_team_meeting, format_for_tasks, _update_sheet

class TestMeetingToolService:
    def test_format_for_tasks(self):
        # Given
        tasks = [
            {"name": "Alice", "task": "Backend Dev"},
            {"name": "Bob", "task": "Frontend Dev"}
        ]
        
        # When
        result = format_for_tasks(tasks)
        
        # Then
        assert "- (Alice) Backend Dev" in result
        assert "- (Bob) Frontend Dev" in result

    def test_format_for_tasks_empty(self):
        assert format_for_tasks([]) == ""
        assert format_for_tasks(None) == ""

    @patch("src.services.meeting_tool_service.meeting_tool_service._parse_with_open_ai")
    @patch("src.services.meeting_tool_service.meeting_tool_service._update_sheet")
    def test_process_team_meeting_success(self, mock_update_sheet, mock_parse):
        # Given
        content = "Meeting content"
        mock_parse.return_value = {
            "global": {
                "일자": "2024-01-01",
                "DONE": "Done tasks",
                "TO DO": "Todo tasks",
                "ISSUE": "Issues"
            }
        }
        mock_update_sheet.return_value = {"status": "success"}

        # When
        result = process_team_meeting(content)

        # Then
        assert result["status"] == "success"
        mock_parse.assert_called_once()
        mock_update_sheet.assert_called_once()

    @patch("src.services.meeting_tool_service.meeting_tool_service.auth")
    @patch("src.services.meeting_tool_service.meeting_tool_service.mkfile")
    @patch("src.services.meeting_tool_service.meeting_tool_service.append_datas_to_spreadsheet")
    def test_update_sheet_success(self, mock_append, mock_mkfile, mock_auth):
        # Given
        rows = [["data"]]
        mock_file_result = MagicMock()
        mock_file_result.id = "spreadsheet_id"
        mock_mkfile.return_value = mock_file_result
        
        mock_append_result = MagicMock()
        mock_append_result.result = "updated"
        mock_append_result.message = "ok"
        mock_append_result.id = "spreadsheet_id"
        mock_append.return_value = mock_append_result

        # When
        result = _update_sheet(rows)

        # Then
        assert result["status"] == "success"
        assert result["id"] == "spreadsheet_id"

    @patch("src.services.meeting_tool_service.meeting_tool_service.auth")
    def test_update_sheet_failure(self, mock_auth):
        # Given
        mock_auth.side_effect = Exception("Auth failed")

        # When
        result = _update_sheet([["data"]])

        # Then
        assert result["status"] == "error"
        assert "Auth failed" in result["message"]
