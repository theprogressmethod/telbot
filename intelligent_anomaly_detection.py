#!/usr/bin/env python3
"""
Progress Method - Intelligent Anomaly Detection System
Advanced anomaly detection, root cause analysis, and automated response
"""

import asyncio
import json
import logging
import statistics
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from supabase import Client

logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    PERFORMANCE = "performance"
    BEHAVIOR = "behavior"
    SECURITY = "security"
    BUSINESS = "business"
    SYSTEM = "system"
    DATA_QUALITY = "data_quality"

class AnomalyLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DetectionMethod(Enum):
    STATISTICAL = "statistical"
    MACHINE_LEARNING = "machine_learning"
    RULE_BASED = "rule_based"
    ENSEMBLE = "ensemble"
    TIME_SERIES = "time_series"

class AnomalyStatus(Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class AnomalySignal:
    signal_id: str
    metric_name: str
    current_value: float
    expected_value: float
    deviation_score: float
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Anomaly:
    anomaly_id: str
    title: str
    description: str
    anomaly_type: AnomalyType
    severity: AnomalyLevel
    detection_method: DetectionMethod
    confidence_score: float
    signals: List[AnomalySignal]
    affected_components: List[str]
    root_cause_hypotheses: List[str]
    impact_assessment: Dict[str, float]
    detection_timestamp: datetime
    status: AnomalyStatus = AnomalyStatus.DETECTED
    resolved_timestamp: Optional[datetime] = None
    false_positive_reason: Optional[str] = None
    response_actions: List[str] = None
    
    def __post_init__(self):
        if self.response_actions is None:
            self.response_actions = []

@dataclass
class AnomalyPattern:
    pattern_id: str
    name: str
    description: str
    detection_criteria: Dict[str, Any]
    statistical_thresholds: Dict[str, float]
    ml_model_parameters: Dict[str, Any]
    historical_occurrences: int
    average_duration_minutes: float
    typical_resolution_actions: List[str]
    created_at: datetime
    last_updated: datetime

@dataclass
class RootCauseAnalysis:
    analysis_id: str
    anomaly_id: str
    investigation_method: str
    contributing_factors: List[Dict[str, Any]]
    correlation_analysis: Dict[str, float]
    timeline_analysis: List[Dict[str, Any]]
    probable_causes: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    recommended_actions: List[str]
    analysis_timestamp: datetime

@dataclass
class AutomatedResponse:
    response_id: str
    anomaly_id: str
    action_type: str
    action_description: str
    execution_status: str
    executed_at: datetime
    execution_result: Dict[str, Any]
    effectiveness_score: Optional[float] = None

class IntelligentAnomalyDetection:
    """Advanced anomaly detection with intelligent analysis and response"""
    
    def __init__(self, supabase_client: Client, metrics_system=None, alerting_system=None):
        self.supabase = supabase_client
        self.metrics = metrics_system
        self.alerting = alerting_system
        
        self.detection_models = {}
        self.anomaly_patterns = {}
        self.active_anomalies = {}
        self.anomaly_history = []
        self.response_automations = {}
        self.baseline_profiles = {}
        
        # Initialize detection system
        self._initialize_detection_models()
        self._initialize_anomaly_patterns()
        self._initialize_automated_responses()
    
    def _initialize_detection_models(self):
        """Initialize anomaly detection models"""
        
        # Statistical detection models
        self.detection_models["statistical"] = {
            "z_score_threshold": 3.0,
            "iqr_multiplier": 1.5,
            "rolling_window_size": 50,
            "seasonal_adjustment": True
        }
        
        # ML-based detection models
        self.detection_models["isolation_forest"] = {
            "contamination": 0.1,
            "n_estimators": 100,
            "max_samples": "auto",
            "random_state": 42
        }
        
        # Time series detection models
        self.detection_models["time_series"] = {
            "seasonal_decomposition": True,
            "trend_detection": True,
            "change_point_detection": True,
            "forecast_horizon": 24  # hours
        }
        
        # Business logic detection
        self.detection_models["business_rules"] = {
            "user_behavior_thresholds": {
                "engagement_drop_percent": 30.0,
                "completion_rate_drop": 0.2,
                "churn_risk_threshold": 0.7
            },
            "system_performance_thresholds": {
                "response_time_multiplier": 3.0,
                "error_rate_threshold": 0.05,
                "throughput_drop_percent": 50.0
            }
        }
        
        logger.info(f"✅ Initialized {len(self.detection_models)} detection models")
    
    def _initialize_anomaly_patterns(self):
        """Initialize known anomaly patterns for rapid detection"""
        
        patterns = [
            AnomalyPattern(
                pattern_id="performance_degradation",
                name="System Performance Degradation",
                description="Gradual or sudden decrease in system performance metrics",
                detection_criteria={
                    "metrics": ["response_time", "throughput", "error_rate"],
                    "threshold_type": "percentage_increase",
                    "threshold_value": 50.0,
                    "duration_minutes": 10
                },
                statistical_thresholds={
                    "z_score": 2.5,
                    "confidence_interval": 0.95
                },
                ml_model_parameters={
                    "model_type": "isolation_forest",
                    "sensitivity": 0.15
                },
                historical_occurrences=15,
                average_duration_minutes=45.0,
                typical_resolution_actions=[
                    "Scale up resources",
                    "Restart affected services",
                    "Check database performance",
                    "Review recent deployments"
                ],
                created_at=datetime.now(),
                last_updated=datetime.now()
            ),
            
            AnomalyPattern(
                pattern_id="user_engagement_drop",
                name="User Engagement Anomaly",
                description="Unusual decrease in user engagement metrics",
                detection_criteria={
                    "metrics": ["dau", "session_duration", "completion_rate"],
                    "threshold_type": "percentage_decrease",
                    "threshold_value": 25.0,
                    "duration_minutes": 60
                },
                statistical_thresholds={
                    "z_score": 2.0,
                    "trend_significance": 0.05
                },
                ml_model_parameters={
                    "model_type": "ensemble",
                    "sensitivity": 0.2
                },
                historical_occurrences=8,
                average_duration_minutes=120.0,
                typical_resolution_actions=[
                    "Analyze recent feature changes",
                    "Check user feedback",
                    "Review user journey analytics",
                    "Implement engagement boosters"
                ],
                created_at=datetime.now(),
                last_updated=datetime.now()
            ),
            
            AnomalyPattern(
                pattern_id="data_quality_anomaly",
                name="Data Quality Issues",
                description="Inconsistencies or abnormalities in data patterns",
                detection_criteria={
                    "metrics": ["data_completeness", "data_consistency", "data_freshness"],
                    "threshold_type": "absolute_threshold",
                    "threshold_value": 0.85,
                    "comparison": "less_than"
                },
                statistical_thresholds={
                    "completeness_threshold": 0.95,
                    "consistency_threshold": 0.98
                },
                ml_model_parameters={
                    "model_type": "statistical",
                    "outlier_detection": True
                },
                historical_occurrences=5,
                average_duration_minutes=90.0,
                typical_resolution_actions=[
                    "Validate data sources",
                    "Check ETL processes",
                    "Review data collection logic",
                    "Implement data quality fixes"
                ],
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
        ]
        
        for pattern in patterns:
            self.anomaly_patterns[pattern.pattern_id] = pattern
        
        logger.info(f"✅ Initialized {len(patterns)} anomaly patterns")
    
    def _initialize_automated_responses(self):
        """Initialize automated response actions"""
        
        self.response_automations = {
            "performance_degradation": [
                {
                    "action": "auto_scale_resources",
                    "conditions": {"severity": ["high", "critical"]},
                    "parameters": {"scale_factor": 1.3, "max_instances": 5}
                },
                {
                    "action": "send_alert_notification",
                    "conditions": {"severity": ["medium", "high", "critical"]},
                    "parameters": {"channels": ["email", "slack"]}
                }
            ],
            "user_engagement_drop": [
                {
                    "action": "trigger_engagement_analysis", 
                    "conditions": {"severity": ["medium", "high"]},
                    "parameters": {"analysis_depth": "comprehensive"}
                },
                {
                    "action": "activate_retention_campaigns",
                    "conditions": {"severity": ["high", "critical"]},
                    "parameters": {"campaign_type": "emergency_retention"}
                }
            ],
            "data_quality_anomaly": [
                {
                    "action": "pause_affected_processes",
                    "conditions": {"severity": ["critical"]},
                    "parameters": {"processes": ["analytics", "reporting"]}
                },
                {
                    "action": "trigger_data_validation",
                    "conditions": {"severity": ["medium", "high", "critical"]},
                    "parameters": {"validation_scope": "full"}
                }
            ]
        }
        
        logger.info("✅ Automated response actions initialized")
    
    async def detect_anomalies(self) -> Dict[str, Any]:
        """Main anomaly detection pipeline"""
        try:
            # Collect current metrics for analysis
            metrics_data = await self._collect_metrics_for_analysis()
            if not metrics_data:
                return {"error": "No metrics data available for analysis"}
            
            # Update baseline profiles
            await self._update_baseline_profiles(metrics_data)
            
            # Apply different detection methods
            statistical_anomalies = await self._statistical_anomaly_detection(metrics_data)
            ml_anomalies = await self._ml_anomaly_detection(metrics_data)
            pattern_anomalies = await self._pattern_based_detection(metrics_data)
            business_anomalies = await self._business_rule_detection(metrics_data)
            
            # Combine and deduplicate anomalies
            all_detected_anomalies = (
                statistical_anomalies + ml_anomalies + 
                pattern_anomalies + business_anomalies
            )
            
            unique_anomalies = await self._deduplicate_anomalies(all_detected_anomalies)
            
            # Perform root cause analysis for high-severity anomalies
            analyzed_anomalies = []
            for anomaly in unique_anomalies:
                if anomaly.severity in [AnomalyLevel.HIGH, AnomalyLevel.CRITICAL]:
                    root_cause = await self._perform_root_cause_analysis(anomaly)
                    anomaly.root_cause_hypotheses = root_cause.probable_causes if root_cause else []
                
                analyzed_anomalies.append(anomaly)
                self.active_anomalies[anomaly.anomaly_id] = anomaly
            
            # Execute automated responses
            response_results = await self._execute_automated_responses(analyzed_anomalies)
            
            # Store in history
            self.anomaly_history.extend(analyzed_anomalies)
            
            return {
                "detection_timestamp": datetime.now().isoformat(),
                "anomalies_detected": len(analyzed_anomalies),
                "anomalies": [asdict(anomaly) for anomaly in analyzed_anomalies],
                "detection_methods_used": ["statistical", "ml", "pattern_based", "business_rules"],
                "severity_distribution": {
                    severity.value: len([a for a in analyzed_anomalies if a.severity == severity])
                    for severity in AnomalyLevel
                },
                "automated_responses_executed": len(response_results),
                "response_results": response_results,
                "total_active_anomalies": len(self.active_anomalies)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in anomaly detection pipeline: {e}")
            return {"error": str(e)}
    
    async def _collect_metrics_for_analysis(self) -> Optional[Dict[str, Any]]:
        """Collect metrics data for anomaly analysis"""
        try:
            metrics_data = {}
            
            # Get system metrics from metrics system
            if self.metrics:
                custom_metrics = await self.metrics.collect_progress_method_metrics()
                for metric in custom_metrics:
                    metrics_data[metric.id] = {
                        "value": metric.value,
                        "timestamp": metric.timestamp.isoformat(),
                        "unit": metric.unit,
                        "tags": metric.tags
                    }
            
            # Add synthetic metrics for demonstration
            current_time = datetime.now()
            synthetic_metrics = {
                "system_response_time": {
                    "value": self._generate_synthetic_metric("response_time", 200, 50),
                    "timestamp": current_time.isoformat(),
                    "unit": "milliseconds",
                    "tags": {"category": "performance"}
                },
                "database_connections": {
                    "value": self._generate_synthetic_metric("db_connections", 25, 10),
                    "timestamp": current_time.isoformat(),
                    "unit": "connections",
                    "tags": {"category": "system"}
                },
                "error_rate": {
                    "value": self._generate_synthetic_metric("error_rate", 0.02, 0.01),
                    "timestamp": current_time.isoformat(),
                    "unit": "percentage",
                    "tags": {"category": "quality"}
                }
            }
            
            metrics_data.update(synthetic_metrics)
            
            return metrics_data
            
        except Exception as e:
            logger.error(f"Error collecting metrics for analysis: {e}")
            return None
    
    def _generate_synthetic_metric(self, metric_type: str, base_value: float, variance: float) -> float:
        """Generate synthetic metric values with potential anomalies"""
        import random
        
        # Seed based on current time for variability
        random.seed(int(datetime.now().timestamp()) % 10000)
        
        # Normal variation
        normal_value = base_value + random.uniform(-variance, variance)
        
        # Occasionally introduce anomalies
        if random.random() < 0.15:  # 15% chance of anomaly
            if metric_type == "response_time":
                return normal_value * random.uniform(2.0, 4.0)  # Spike
            elif metric_type == "error_rate":
                return normal_value * random.uniform(3.0, 8.0)  # Error spike
            elif metric_type == "db_connections":
                return normal_value * random.uniform(1.5, 3.0)  # Connection surge
        
        return max(0, normal_value)
    
    async def _update_baseline_profiles(self, metrics_data: Dict[str, Any]):
        """Update baseline profiles for metrics"""
        try:
            for metric_name, metric_info in metrics_data.items():
                if metric_name not in self.baseline_profiles:
                    # Initialize new baseline
                    self.baseline_profiles[metric_name] = {
                        "values_history": [metric_info["value"]],
                        "mean": metric_info["value"],
                        "std": 0.0,
                        "min": metric_info["value"],
                        "max": metric_info["value"],
                        "last_updated": datetime.now()
                    }
                else:
                    # Update existing baseline
                    baseline = self.baseline_profiles[metric_name]
                    baseline["values_history"].append(metric_info["value"])
                    
                    # Keep only recent history (last 100 values)
                    if len(baseline["values_history"]) > 100:
                        baseline["values_history"] = baseline["values_history"][-100:]
                    
                    # Recalculate statistics
                    values = baseline["values_history"]
                    baseline["mean"] = statistics.mean(values)
                    baseline["std"] = statistics.stdev(values) if len(values) > 1 else 0.0
                    baseline["min"] = min(values)
                    baseline["max"] = max(values)
                    baseline["last_updated"] = datetime.now()
                    
        except Exception as e:
            logger.error(f"Error updating baseline profiles: {e}")
    
    async def _statistical_anomaly_detection(self, metrics_data: Dict[str, Any]) -> List[Anomaly]:
        """Statistical anomaly detection using Z-score and IQR methods"""
        try:
            anomalies = []
            model_params = self.detection_models["statistical"]
            z_threshold = model_params["z_score_threshold"]
            
            for metric_name, metric_info in metrics_data.items():
                baseline = self.baseline_profiles.get(metric_name)
                if not baseline or baseline["std"] == 0:
                    continue  # Skip if no baseline or no variation
                
                current_value = metric_info["value"]
                mean = baseline["mean"]
                std = baseline["std"]
                
                # Calculate Z-score
                z_score = abs(current_value - mean) / std
                
                if z_score > z_threshold:
                    # Statistical anomaly detected
                    signal = AnomalySignal(
                        signal_id=str(uuid.uuid4()),
                        metric_name=metric_name,
                        current_value=current_value,
                        expected_value=mean,
                        deviation_score=z_score,
                        timestamp=datetime.now(),
                        metadata={"detection_method": "z_score", "threshold": z_threshold}
                    )
                    
                    # Determine severity based on Z-score
                    if z_score > 4.0:
                        severity = AnomalyLevel.CRITICAL
                    elif z_score > 3.5:
                        severity = AnomalyLevel.HIGH
                    elif z_score > 3.0:
                        severity = AnomalyLevel.MEDIUM
                    else:
                        severity = AnomalyLevel.LOW
                    
                    anomaly = Anomaly(
                        anomaly_id=str(uuid.uuid4()),
                        title=f"Statistical Anomaly: {metric_name}",
                        description=f"{metric_name} value {current_value} deviates significantly from baseline (Z-score: {z_score:.2f})",
                        anomaly_type=AnomalyType.SYSTEM,
                        severity=severity,
                        detection_method=DetectionMethod.STATISTICAL,
                        confidence_score=min(1.0, z_score / 5.0),
                        signals=[signal],
                        affected_components=[metric_name],
                        root_cause_hypotheses=[],
                        impact_assessment={"deviation_magnitude": z_score},
                        detection_timestamp=datetime.now()
                    )
                    
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in statistical anomaly detection: {e}")
            return []
    
    async def _ml_anomaly_detection(self, metrics_data: Dict[str, Any]) -> List[Anomaly]:
        """Machine learning-based anomaly detection"""
        try:
            anomalies = []
            
            # Simulate ML model predictions (in production, use trained models)
            for metric_name, metric_info in metrics_data.items():
                baseline = self.baseline_profiles.get(metric_name)
                if not baseline:
                    continue
                
                current_value = metric_info["value"]
                
                # Simulate isolation forest prediction
                anomaly_score = self._simulate_ml_anomaly_score(metric_name, current_value, baseline)
                
                # Threshold for anomaly detection
                if anomaly_score > 0.6:  # Anomaly threshold
                    signal = AnomalySignal(
                        signal_id=str(uuid.uuid4()),
                        metric_name=metric_name,
                        current_value=current_value,
                        expected_value=baseline["mean"],
                        deviation_score=anomaly_score,
                        timestamp=datetime.now(),
                        metadata={"detection_method": "isolation_forest", "anomaly_score": anomaly_score}
                    )
                    
                    # Determine severity based on ML score
                    if anomaly_score > 0.9:
                        severity = AnomalyLevel.CRITICAL
                    elif anomaly_score > 0.8:
                        severity = AnomalyLevel.HIGH
                    elif anomaly_score > 0.7:
                        severity = AnomalyLevel.MEDIUM
                    else:
                        severity = AnomalyLevel.LOW
                    
                    anomaly = Anomaly(
                        anomaly_id=str(uuid.uuid4()),
                        title=f"ML Anomaly: {metric_name}",
                        description=f"Machine learning model detected anomaly in {metric_name} (score: {anomaly_score:.2f})",
                        anomaly_type=AnomalyType.SYSTEM,
                        severity=severity,
                        detection_method=DetectionMethod.MACHINE_LEARNING,
                        confidence_score=anomaly_score,
                        signals=[signal],
                        affected_components=[metric_name],
                        root_cause_hypotheses=[],
                        impact_assessment={"ml_anomaly_score": anomaly_score},
                        detection_timestamp=datetime.now()
                    )
                    
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in ML anomaly detection: {e}")
            return []
    
    def _simulate_ml_anomaly_score(self, metric_name: str, current_value: float, baseline: Dict[str, Any]) -> float:
        """Simulate ML model anomaly scoring"""
        try:
            # Simple anomaly scoring based on distance from baseline
            mean = baseline["mean"]
            std = baseline["std"]
            
            if std == 0:
                return 0.0
            
            # Normalized distance from mean
            normalized_distance = abs(current_value - mean) / (3 * std)  # 3-sigma normalization
            
            # Convert to anomaly score (0-1 scale)
            anomaly_score = min(1.0, normalized_distance)
            
            # Add some randomness to simulate ML model uncertainty
            import random
            random.seed(hash(metric_name) % 1000)
            noise = random.uniform(-0.1, 0.1)
            
            return max(0.0, min(1.0, anomaly_score + noise))
            
        except Exception as e:
            logger.error(f"Error simulating ML anomaly score: {e}")
            return 0.0
    
    async def _pattern_based_detection(self, metrics_data: Dict[str, Any]) -> List[Anomaly]:
        """Pattern-based anomaly detection using known patterns"""
        try:
            anomalies = []
            
            # Check each known pattern
            for pattern_id, pattern in self.anomaly_patterns.items():
                pattern_match = await self._check_pattern_match(pattern, metrics_data)
                
                if pattern_match:
                    signals = []
                    for metric_name in pattern_match["matching_metrics"]:
                        if metric_name in metrics_data:
                            signal = AnomalySignal(
                                signal_id=str(uuid.uuid4()),
                                metric_name=metric_name,
                                current_value=metrics_data[metric_name]["value"],
                                expected_value=pattern_match["expected_values"].get(metric_name, 0),
                                deviation_score=pattern_match["pattern_strength"],
                                timestamp=datetime.now(),
                                metadata={"pattern_id": pattern_id, "pattern_name": pattern.name}
                            )
                            signals.append(signal)
                    
                    anomaly = Anomaly(
                        anomaly_id=str(uuid.uuid4()),
                        title=f"Pattern Anomaly: {pattern.name}",
                        description=f"Detected known anomaly pattern: {pattern.description}",
                        anomaly_type=AnomalyType.PERFORMANCE if "performance" in pattern_id else AnomalyType.BEHAVIOR,
                        severity=self._determine_pattern_severity(pattern_match["pattern_strength"]),
                        detection_method=DetectionMethod.RULE_BASED,
                        confidence_score=pattern_match["pattern_strength"],
                        signals=signals,
                        affected_components=pattern_match["matching_metrics"],
                        root_cause_hypotheses=pattern.typical_resolution_actions,
                        impact_assessment={"pattern_strength": pattern_match["pattern_strength"]},
                        detection_timestamp=datetime.now()
                    )
                    
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in pattern-based detection: {e}")
            return []
    
    async def _check_pattern_match(self, pattern: AnomalyPattern, metrics_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if current metrics match a known anomaly pattern"""
        try:
            criteria = pattern.detection_criteria
            matching_metrics = []
            pattern_strength = 0.0
            expected_values = {}
            
            for metric_name in criteria.get("metrics", []):
                if metric_name not in metrics_data:
                    continue
                
                baseline = self.baseline_profiles.get(metric_name)
                if not baseline:
                    continue
                
                current_value = metrics_data[metric_name]["value"]
                baseline_value = baseline["mean"]
                expected_values[metric_name] = baseline_value
                
                # Check pattern criteria
                threshold_type = criteria.get("threshold_type")
                threshold_value = criteria.get("threshold_value", 0)
                
                if threshold_type == "percentage_increase":
                    percent_change = ((current_value - baseline_value) / baseline_value * 100) if baseline_value != 0 else 0
                    if percent_change >= threshold_value:
                        matching_metrics.append(metric_name)
                        pattern_strength += min(1.0, percent_change / 100.0)
                
                elif threshold_type == "percentage_decrease":
                    percent_change = ((baseline_value - current_value) / baseline_value * 100) if baseline_value != 0 else 0
                    if percent_change >= threshold_value:
                        matching_metrics.append(metric_name)
                        pattern_strength += min(1.0, percent_change / 100.0)
                
                elif threshold_type == "absolute_threshold":
                    comparison = criteria.get("comparison", "greater_than")
                    if comparison == "greater_than" and current_value > threshold_value:
                        matching_metrics.append(metric_name)
                        pattern_strength += 0.8
                    elif comparison == "less_than" and current_value < threshold_value:
                        matching_metrics.append(metric_name)
                        pattern_strength += 0.8
            
            # Normalize pattern strength
            if matching_metrics:
                pattern_strength = min(1.0, pattern_strength / len(matching_metrics))
                
                # Require minimum pattern strength and matching metrics
                if pattern_strength > 0.5 and len(matching_metrics) >= 1:
                    return {
                        "matching_metrics": matching_metrics,
                        "pattern_strength": pattern_strength,
                        "expected_values": expected_values
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking pattern match: {e}")
            return None
    
    def _determine_pattern_severity(self, pattern_strength: float) -> AnomalyLevel:
        """Determine severity based on pattern strength"""
        if pattern_strength > 0.9:
            return AnomalyLevel.CRITICAL
        elif pattern_strength > 0.8:
            return AnomalyLevel.HIGH
        elif pattern_strength > 0.6:
            return AnomalyLevel.MEDIUM
        else:
            return AnomalyLevel.LOW
    
    async def _business_rule_detection(self, metrics_data: Dict[str, Any]) -> List[Anomaly]:
        """Business rule-based anomaly detection"""
        try:
            anomalies = []
            business_rules = self.detection_models["business_rules"]
            
            # Check user behavior thresholds
            behavior_thresholds = business_rules["user_behavior_thresholds"]
            
            # Check for engagement drops
            if "dau" in metrics_data:
                current_dau = metrics_data["dau"]["value"]
                baseline = self.baseline_profiles.get("dau")
                
                if baseline:
                    baseline_dau = baseline["mean"]
                    if baseline_dau > 0:
                        drop_percent = ((baseline_dau - current_dau) / baseline_dau * 100)
                        
                        if drop_percent >= behavior_thresholds["engagement_drop_percent"]:
                            signal = AnomalySignal(
                                signal_id=str(uuid.uuid4()),
                                metric_name="dau",
                                current_value=current_dau,
                                expected_value=baseline_dau,
                                deviation_score=drop_percent / 100,
                                timestamp=datetime.now(),
                                metadata={"rule": "engagement_drop", "drop_percent": drop_percent}
                            )
                            
                            anomaly = Anomaly(
                                anomaly_id=str(uuid.uuid4()),
                                title="Business Rule Anomaly: User Engagement Drop",
                                description=f"Daily active users dropped by {drop_percent:.1f}% below baseline",
                                anomaly_type=AnomalyType.BUSINESS,
                                severity=AnomalyLevel.HIGH if drop_percent > 50 else AnomalyLevel.MEDIUM,
                                detection_method=DetectionMethod.RULE_BASED,
                                confidence_score=min(1.0, drop_percent / 50),
                                signals=[signal],
                                affected_components=["user_engagement"],
                                root_cause_hypotheses=[
                                    "Recent feature changes affecting user experience",
                                    "Technical issues impacting accessibility",
                                    "External factors affecting user behavior"
                                ],
                                impact_assessment={"engagement_drop_percent": drop_percent},
                                detection_timestamp=datetime.now()
                            )
                            
                            anomalies.append(anomaly)
            
            # Check system performance thresholds
            perf_thresholds = business_rules["system_performance_thresholds"]
            
            if "system_response_time" in metrics_data:
                current_rt = metrics_data["system_response_time"]["value"]
                baseline = self.baseline_profiles.get("system_response_time")
                
                if baseline:
                    baseline_rt = baseline["mean"]
                    multiplier = current_rt / baseline_rt if baseline_rt > 0 else 1
                    
                    if multiplier >= perf_thresholds["response_time_multiplier"]:
                        signal = AnomalySignal(
                            signal_id=str(uuid.uuid4()),
                            metric_name="system_response_time",
                            current_value=current_rt,
                            expected_value=baseline_rt,
                            deviation_score=multiplier,
                            timestamp=datetime.now(),
                            metadata={"rule": "response_time_spike", "multiplier": multiplier}
                        )
                        
                        anomaly = Anomaly(
                            anomaly_id=str(uuid.uuid4()),
                            title="Business Rule Anomaly: Response Time Spike",
                            description=f"Response time is {multiplier:.1f}x higher than baseline",
                            anomaly_type=AnomalyType.PERFORMANCE,
                            severity=AnomalyLevel.CRITICAL if multiplier > 5 else AnomalyLevel.HIGH,
                            detection_method=DetectionMethod.RULE_BASED,
                            confidence_score=min(1.0, multiplier / 5),
                            signals=[signal],
                            affected_components=["api_performance"],
                            root_cause_hypotheses=[
                                "Database performance issues",
                                "Resource constraints",
                                "External service dependencies",
                                "Code performance regression"
                            ],
                            impact_assessment={"performance_degradation_factor": multiplier},
                            detection_timestamp=datetime.now()
                        )
                        
                        anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in business rule detection: {e}")
            return []
    
    async def _deduplicate_anomalies(self, anomalies: List[Anomaly]) -> List[Anomaly]:
        """Remove duplicate anomalies and merge similar ones"""
        try:
            if not anomalies:
                return anomalies
            
            unique_anomalies = []
            processed_metrics = set()
            
            # Sort by severity and confidence
            sorted_anomalies = sorted(
                anomalies, 
                key=lambda a: (a.severity.value, -a.confidence_score), 
                reverse=True
            )
            
            for anomaly in sorted_anomalies:
                # Check if we already have an anomaly for the same metric(s)
                affected_metrics = set(anomaly.affected_components)
                
                if not affected_metrics.intersection(processed_metrics):
                    unique_anomalies.append(anomaly)
                    processed_metrics.update(affected_metrics)
                else:
                    # Merge with existing anomaly if similar
                    for existing_anomaly in unique_anomalies:
                        existing_metrics = set(existing_anomaly.affected_components)
                        if affected_metrics.intersection(existing_metrics):
                            # Merge signals and update confidence
                            existing_anomaly.signals.extend(anomaly.signals)
                            existing_anomaly.confidence_score = max(
                                existing_anomaly.confidence_score,
                                anomaly.confidence_score
                            )
                            break
            
            return unique_anomalies
            
        except Exception as e:
            logger.error(f"Error deduplicating anomalies: {e}")
            return anomalies
    
    async def _perform_root_cause_analysis(self, anomaly: Anomaly) -> Optional[RootCauseAnalysis]:
        """Perform root cause analysis for high-priority anomalies"""
        try:
            # Simulate root cause analysis
            analysis = RootCauseAnalysis(
                analysis_id=str(uuid.uuid4()),
                anomaly_id=anomaly.anomaly_id,
                investigation_method="automated_correlation",
                contributing_factors=[],
                correlation_analysis={},
                timeline_analysis=[],
                probable_causes=[],
                confidence_scores={},
                recommended_actions=[],
                analysis_timestamp=datetime.now()
            )
            
            # Analyze contributing factors based on anomaly type
            if anomaly.anomaly_type == AnomalyType.PERFORMANCE:
                analysis.contributing_factors = [
                    {"factor": "resource_utilization", "impact_score": 0.8},
                    {"factor": "database_performance", "impact_score": 0.6},
                    {"factor": "external_dependencies", "impact_score": 0.4}
                ]
                
                analysis.probable_causes = [
                    {"cause": "High resource utilization", "probability": 0.7},
                    {"cause": "Database query performance degradation", "probability": 0.6},
                    {"cause": "External API latency", "probability": 0.3}
                ]
                
                analysis.recommended_actions = [
                    "Scale up system resources",
                    "Optimize database queries",
                    "Check external service status",
                    "Review recent code deployments"
                ]
            
            elif anomaly.anomaly_type == AnomalyType.BUSINESS:
                analysis.contributing_factors = [
                    {"factor": "user_behavior_change", "impact_score": 0.9},
                    {"factor": "feature_changes", "impact_score": 0.7},
                    {"factor": "external_events", "impact_score": 0.5}
                ]
                
                analysis.probable_causes = [
                    {"cause": "Recent feature changes affecting user experience", "probability": 0.8},
                    {"cause": "User interface modifications", "probability": 0.6},
                    {"cause": "External market factors", "probability": 0.3}
                ]
                
                analysis.recommended_actions = [
                    "Analyze user feedback and support tickets",
                    "Review recent feature releases",
                    "Conduct user behavior analysis",
                    "Implement user retention strategies"
                ]
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error performing root cause analysis: {e}")
            return None
    
    async def _execute_automated_responses(self, anomalies: List[Anomaly]) -> List[Dict[str, Any]]:
        """Execute automated responses for detected anomalies"""
        try:
            response_results = []
            
            for anomaly in anomalies:
                # Find matching response automations
                automation_key = None
                
                # Map anomaly characteristics to automation keys
                if anomaly.anomaly_type == AnomalyType.PERFORMANCE:
                    automation_key = "performance_degradation"
                elif anomaly.anomaly_type == AnomalyType.BUSINESS:
                    automation_key = "user_engagement_drop"
                elif anomaly.anomaly_type == AnomalyType.DATA_QUALITY:
                    automation_key = "data_quality_anomaly"
                
                if automation_key and automation_key in self.response_automations:
                    automations = self.response_automations[automation_key]
                    
                    for automation in automations:
                        # Check if conditions are met
                        conditions = automation.get("conditions", {})
                        severity_conditions = conditions.get("severity", [])
                        
                        if not severity_conditions or anomaly.severity.value in severity_conditions:
                            # Execute automated response
                            response = await self._execute_single_response(anomaly, automation)
                            response_results.append(response)
            
            return response_results
            
        except Exception as e:
            logger.error(f"Error executing automated responses: {e}")
            return []
    
    async def _execute_single_response(self, anomaly: Anomaly, automation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single automated response action"""
        try:
            action_type = automation["action"]
            parameters = automation.get("parameters", {})
            
            response = AutomatedResponse(
                response_id=str(uuid.uuid4()),
                anomaly_id=anomaly.anomaly_id,
                action_type=action_type,
                action_description=f"Automated {action_type} for {anomaly.title}",
                execution_status="executing",
                executed_at=datetime.now(),
                execution_result={}
            )
            
            # Simulate response execution
            if action_type == "send_alert_notification":
                response.execution_result = {
                    "notifications_sent": len(parameters.get("channels", [])),
                    "channels": parameters.get("channels", []),
                    "success": True
                }
                response.execution_status = "completed"
                response.effectiveness_score = 0.9
                
            elif action_type == "auto_scale_resources":
                response.execution_result = {
                    "scale_factor_applied": parameters.get("scale_factor", 1.0),
                    "max_instances": parameters.get("max_instances", 3),
                    "scaling_triggered": True,
                    "success": True
                }
                response.execution_status = "completed"
                response.effectiveness_score = 0.8
                
            elif action_type == "trigger_engagement_analysis":
                response.execution_result = {
                    "analysis_initiated": True,
                    "analysis_depth": parameters.get("analysis_depth", "basic"),
                    "estimated_completion": "15_minutes",
                    "success": True
                }
                response.execution_status = "completed"
                response.effectiveness_score = 0.7
                
            else:
                response.execution_result = {"action_simulated": True, "success": True}
                response.execution_status = "completed"
                response.effectiveness_score = 0.6
            
            # Store response
            anomaly.response_actions.append(action_type)
            
            return asdict(response)
            
        except Exception as e:
            logger.error(f"Error executing single response: {e}")
            return {"error": str(e)}
    
    async def get_anomaly_detection_status(self) -> Dict[str, Any]:
        """Get current anomaly detection system status"""
        try:
            active_anomalies_count = len(self.active_anomalies)
            total_patterns = len(self.anomaly_patterns)
            detection_models_count = len(self.detection_models)
            
            # Calculate anomaly statistics
            recent_anomalies = [
                a for a in self.anomaly_history 
                if a.detection_timestamp > datetime.now() - timedelta(hours=24)
            ]
            
            severity_distribution = {}
            for severity in AnomalyLevel:
                count = len([a for a in recent_anomalies if a.severity == severity])
                severity_distribution[severity.value] = count
            
            # Response automation statistics
            total_automations = sum(len(actions) for actions in self.response_automations.values())
            
            return {
                "system_status": "operational",
                "detection_capabilities": {
                    "statistical_detection": True,
                    "ml_detection": True,
                    "pattern_based_detection": True,
                    "business_rule_detection": True,
                    "root_cause_analysis": True,
                    "automated_response": True
                },
                "active_anomalies": active_anomalies_count,
                "anomaly_patterns": total_patterns,
                "detection_models": detection_models_count,
                "recent_24h_anomalies": len(recent_anomalies),
                "severity_distribution": severity_distribution,
                "response_automations": total_automations,
                "baseline_profiles": len(self.baseline_profiles),
                "last_detection_run": max([a.detection_timestamp for a in recent_anomalies]).isoformat() if recent_anomalies else None,
                "system_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting anomaly detection status: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    print("Intelligent Anomaly Detection - Advanced anomaly detection and automated response for Progress Method")