from string import Template
from typing import Any, Dict
from .models import NotificationSeverity

# 25+ templates mapping metrics to alerts
TEMPLATES = {
    # Transaction Templates
    "tx_volume_spike": {
        "title": "Transaction Volume Spike",
        "message": Template("Transaction volume for $channel has increased by $percentage% in the last $timeframe."),
        "severity": NotificationSeverity.WARNING,
        "category": "transaction"
    },
    "tx_value_drop": {
        "title": "Transaction Value Drop",
        "message": Template("Total transaction value dropped by $percentage% compared to the benchmark."),
        "severity": NotificationSeverity.CRITICAL,
        "category": "transaction"
    },
    "tx_approval_drop": {
        "title": "Approval Rate Drop",
        "message": Template("Approval rate fell to $rate%, below the $threshold% threshold."),
        "severity": NotificationSeverity.CRITICAL,
        "category": "transaction"
    },
    "tx_decline_spike": {
        "title": "Decline Rate Spike",
        "message": Template("Decline rate spiked to $rate%. Top reason: $top_reason."),
        "severity": NotificationSeverity.WARNING,
        "category": "transaction"
    },
    "tx_geo_anomaly": {
        "title": "Geographic Anomaly",
        "message": Template("Unusual transaction volume detected in $region."),
        "severity": NotificationSeverity.INFO,
        "category": "transaction"
    },
    "tx_peak_time_shift": {
        "title": "Peak Time Shift",
        "message": Template("Peak transaction hours shifted from $old_peak to $new_peak."),
        "severity": NotificationSeverity.INFO,
        "category": "transaction"
    },
    "tx_type_anomaly": {
        "title": "Transaction Type Anomaly",
        "message": Template("Unusual surge in $tx_type transactions."),
        "severity": NotificationSeverity.WARNING,
        "category": "transaction"
    },

    # Card Templates
    "card_issuance_milestone": {
        "title": "Issuance Milestone",
        "message": Template("$count new cards issued this week, exceeding the target."),
        "severity": NotificationSeverity.SUCCESS,
        "category": "cards"
    },
    "card_usage_drop": {
        "title": "Card Usage Drop",
        "message": Template("Active card usage dropped by $percentage%."),
        "severity": NotificationSeverity.WARNING,
        "category": "cards"
    },
    "card_replacement_surge": {
        "title": "Card Replacement Surge",
        "message": Template("High demand for card replacements: $count requests today."),
        "severity": NotificationSeverity.WARNING,
        "category": "cards"
    },
    "card_scheme_performance": {
        "title": "Scheme Performance Alert",
        "message": Template("$scheme transactions are processing $delay% slower than average."),
        "severity": NotificationSeverity.WARNING,
        "category": "cards"
    },

    # Merchant Templates
    "merchant_onboarding_stall": {
        "title": "Onboarding Stalled",
        "message": Template("Merchant onboarding rate decreased to $rate/day."),
        "severity": NotificationSeverity.WARNING,
        "category": "merchants"
    },
    "merchant_pos_growth": {
        "title": "POS Growth Target Hit",
        "message": Template("POS transaction volume grew by $percentage% in $region."),
        "severity": NotificationSeverity.SUCCESS,
        "category": "merchants"
    },
    "merchant_dormant": {
        "title": "Dormant Merchants Increasing",
        "message": Template("$count merchants became dormant this week."),
        "severity": NotificationSeverity.WARNING,
        "category": "merchants"
    },

    # Settlement Templates
    "settlement_delayed": {
        "title": "Settlement Delay",
        "message": Template("Avg settlement time increased to $time hours."),
        "severity": NotificationSeverity.CRITICAL,
        "category": "settlement"
    },
    "settlement_mismatch": {
        "title": "Settlement Accuracy Issue",
        "message": Template("Found $count unsettled transactions beyond SLA."),
        "severity": NotificationSeverity.CRITICAL,
        "category": "settlement"
    },
    
    # Customer Templates
    "customer_churn_risk": {
        "title": "High Churn Risk",
        "message": Template("Predicted churn rate rose to $rate%."),
        "severity": NotificationSeverity.CRITICAL,
        "category": "customer"
    },
    "customer_arpu_drop": {
        "title": "ARPU Drop",
        "message": Template("Average Revenue Per User dropped to $$ $value."),
        "severity": NotificationSeverity.WARNING,
        "category": "customer"
    },
    
    # System & Benchmark Templates
    "sys_benchmark_updated": {
         "title": "Benchmark Updated",
         "message": Template("Rolling averages updated for $metric. New baseline: $value."),
         "severity": NotificationSeverity.INFO,
         "category": "system"
    },
    "sys_job_failure": {
         "title": "Analytics Job Failed",
         "message": Template("Job $job_name failed with error: $error."),
         "severity": NotificationSeverity.CRITICAL,
         "category": "system"
    },
    "sys_db_latency": {
         "title": "Database Latency",
         "message": Template("Analytics DB response time exceeded $threshold ms."),
         "severity": NotificationSeverity.WARNING,
         "category": "system"
    },
    "sys_memory_warning": {
         "title": "High Memory Usage",
         "message": Template("Analytics server memory usage is at $percentage%."),
         "severity": NotificationSeverity.WARNING,
         "category": "system"
    },
    "sys_disk_space": {
         "title": "Low Disk Space",
         "message": Template("Only $percentage% disk space remaining on $drive for benchmarks."),
         "severity": NotificationSeverity.CRITICAL,
         "category": "system"
    },
    "sys_service_restart": {
         "title": "Service Restarted",
         "message": Template("Analytics service $service was restarted automatically."),
         "severity": NotificationSeverity.INFO,
         "category": "system"
    },
    "sys_sse_limit": {
         "title": "SSE Connection Limit",
         "message": Template("Active SSE connections reached $count. Close to maximum."),
         "severity": NotificationSeverity.WARNING,
         "category": "system"
    }
}

class TemplateEngine:
    @staticmethod
    def format_alert(template_key: str, **kwargs: Any) -> Dict[str, Any]:
        if template_key not in TEMPLATES:
            raise ValueError(f"Unknown template key: {template_key}")
            
        tpl = TEMPLATES[template_key]
        try:
            message = tpl["message"].safe_substitute(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter for template {template_key}: {e}")
        
        return {
            "title": tpl["title"],
            "message": message,
            "severity": tpl["severity"],
            "category": tpl["category"],
            "metadata": kwargs
        }
