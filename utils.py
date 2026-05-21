import pandas as pd
import io
from datetime import datetime

def maps_to_excel(maps):
    try:
        df = pd.DataFrame(maps)
        df = df.rename(columns={
            'id': 'MAP ID',
            'action': 'Action Required',
            'department': 'Responsible Department',
            'deadline': 'Deadline',
            'priority': 'Priority',
            'status': 'Current Status',
            'compliance_risk': 'Compliance Risk',
            'estimated_effort': 'Estimated Effort'
        })
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        return buffer
    except Exception as e:
        raise Exception(f"Excel export error: {str(e)}")


def get_summary_stats(maps):
    total = len(maps)
    if total == 0:
        return {}
    return {
        'total': total,
        'high_priority': len([m for m in maps if m.get('priority') == 'High']),
        'medium_priority': len([m for m in maps if m.get('priority') == 'Medium']),
        'low_priority': len([m for m in maps if m.get('priority') == 'Low']),
        'pending': len([m for m in maps if m.get('status') == 'Pending']),
        'in_progress': len([m for m in maps if m.get('status') == 'In Progress']),
        'completed': len([m for m in maps if m.get('status') == 'Completed']),
        'overdue': len([m for m in maps if m.get('status') == 'Overdue']),
        'departments': len(set(m.get('department') for m in maps)),
        'completion_rate': round(
            len([m for m in maps if m.get('status') == 'Completed']) / total * 100, 1
        )
    }


def get_dept_breakdown(maps):
    dept_counts = {}
    for m in maps:
        dept = m.get('department', 'Unknown')
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
    return dept_counts


def get_audit_log_entry(map_id, old_status, new_status):
    return {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'map_id': map_id,
        'old_status': old_status,
        'new_status': new_status,
        'changed_by': 'Compliance Officer'
    }