from datetime import datetime

class MAP:
    """
    Measurable Action Point - ek regulatory task represent karta hai
    """
    
    def __init__(self, id, action, department, deadline, 
                 priority, compliance_risk="", estimated_effort="Medium"):
        # Core data
        self.id = id
        self.action = action
        self.department = department
        self.deadline = deadline
        self.priority = priority
        self.compliance_risk = compliance_risk
        self.estimated_effort = estimated_effort
        
        # Status tracking
        self.status = "Pending"
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at
    
    def update_status(self, new_status):
        """Status update karo aur timestamp save karo"""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return old_status
    
    def is_high_priority(self):
        """High priority hai ya nahi"""
        return self.priority == "High"
    
    def is_completed(self):
        """Complete hua ya nahi"""
        return self.status == "Completed"
    
    def to_dict(self):
        """Class ko dictionary mein convert karo - database ke liye"""
        return {
            'id': self.id,
            'action': self.action,
            'department': self.department,
            'deadline': self.deadline,
            'priority': self.priority,
            'status': self.status,
            'compliance_risk': self.compliance_risk,
            'estimated_effort': self.estimated_effort,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Dictionary se MAP object banao - database se load karne ke liye"""
        obj = cls(
            id=data['id'],
            action=data['action'],
            department=data['department'],
            deadline=data['deadline'],
            priority=data['priority'],
            compliance_risk=data.get('compliance_risk', ''),
            estimated_effort=data.get('estimated_effort', 'Medium')
        )
        obj.status = data.get('status', 'Pending')
        return obj
    
    def __repr__(self):
        """Print karne pe clean output"""
        return f"MAP-{self.id} | {self.department} | {self.status}"


class CircularSession:
    """
    Ek regulatory circular aur uske saare MAPs ko represent karta hai
    """
    
    def __init__(self, circular_text):
        self.circular_text = circular_text
        self.maps = []
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def add_map(self, map_obj):
        """Naya MAP add karo"""
        self.maps.append(map_obj)
    
    def get_by_department(self, department):
        """Department ke saare MAPs lo"""
        return [m for m in self.maps if m.department == department]
    
    def get_high_priority(self):
        """Sirf high priority MAPs lo"""
        return [m for m in self.maps if m.is_high_priority()]
    
    def get_pending(self):
        """Sirf pending MAPs lo"""
        return [m for m in self.maps if m.status == "Pending"]
    
    def completion_rate(self):
        """Kitne percent complete hue"""
        if not self.maps:
            return 0
        completed = len([m for m in self.maps if m.is_completed()])
        return round(completed / len(self.maps) * 100, 1)
    
    def summary(self):
        """Quick summary"""
        return {
            'total': len(self.maps),
            'completed': len([m for m in self.maps if m.is_completed()]),
            'pending': len([m for m in self.maps if m.status == "Pending"]),
            'high_priority': len(self.get_high_priority()),
            'completion_rate': self.completion_rate()
        }