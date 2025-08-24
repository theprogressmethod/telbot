#!/usr/bin/env python3
"""
Progress Method - Auto-scaling and Resource Optimization System
Intelligent resource management, capacity planning, and automatic scaling
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from supabase import Client

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory" 
    DATABASE_CONNECTIONS = "database_connections"
    API_RATE_LIMITS = "api_rate_limits"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"

class ScalingDirection(Enum):
    UP = "scale_up"
    DOWN = "scale_down"
    MAINTAIN = "maintain"

class ScalingTrigger(Enum):
    THRESHOLD_BASED = "threshold_based"
    PREDICTIVE = "predictive"
    SCHEDULE_BASED = "schedule_based"
    MANUAL = "manual"
    EMERGENCY = "emergency"

class ResourceStatus(Enum):
    OPTIMAL = "optimal"
    UNDER_UTILIZED = "under_utilized"
    OVER_UTILIZED = "over_utilized"
    CRITICAL = "critical"

@dataclass
class ResourceMetrics:
    resource_type: ResourceType
    current_usage: float
    capacity: float
    utilization_percentage: float
    trend_direction: str
    peak_usage_24h: float
    avg_usage_7d: float
    timestamp: datetime
    status: ResourceStatus = ResourceStatus.OPTIMAL
    
    def __post_init__(self):
        # Auto-determine status based on utilization
        if self.utilization_percentage > 90:
            self.status = ResourceStatus.CRITICAL
        elif self.utilization_percentage > 75:
            self.status = ResourceStatus.OVER_UTILIZED
        elif self.utilization_percentage < 30:
            self.status = ResourceStatus.UNDER_UTILIZED
        else:
            self.status = ResourceStatus.OPTIMAL

@dataclass
class ScalingRule:
    id: str
    name: str
    resource_type: ResourceType
    trigger_type: ScalingTrigger
    scale_up_threshold: float
    scale_down_threshold: float
    cooldown_minutes: int
    min_capacity: float
    max_capacity: float
    scaling_factor: float  # How much to scale (e.g., 1.5 = 50% increase)
    enabled: bool = True
    priority: int = 1
    conditions: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}

@dataclass
class ScalingAction:
    id: str
    rule_id: str
    resource_type: ResourceType
    direction: ScalingDirection
    trigger: ScalingTrigger
    current_capacity: float
    target_capacity: float
    scaling_factor: float
    reason: str
    confidence_score: float
    estimated_cost_impact: float
    estimated_performance_impact: float
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    status: str = "pending"
    execution_result: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.execution_result is None:
            self.execution_result = {}

@dataclass
class CapacityForecast:
    resource_type: ResourceType
    forecast_horizon_hours: int
    predicted_peak_usage: float
    predicted_avg_usage: float
    confidence_score: float
    recommended_capacity: float
    cost_optimization_opportunities: List[str]
    risk_factors: List[str]
    generated_at: datetime

@dataclass
class ResourceOptimizationRecommendation:
    id: str
    title: str
    description: str
    resource_type: ResourceType
    optimization_type: str  # "rightsizing", "scheduling", "caching", etc.
    current_state: Dict[str, Any]
    recommended_state: Dict[str, Any]
    expected_savings: Dict[str, float]  # cost, performance, etc.
    implementation_complexity: str
    risk_level: str
    prerequisites: List[str]
    created_at: datetime

class AutoScalingSystem:
    """Intelligent auto-scaling and resource optimization system"""
    
    def __init__(self, supabase_client: Client, metrics_system=None, predictive_system=None):
        self.supabase = supabase_client
        self.metrics = metrics_system
        self.predictive = predictive_system
        
        self.scaling_rules = {}
        self.resource_metrics = {}
        self.scaling_actions = []
        self.capacity_forecasts = {}
        self.optimization_recommendations = []
        
        # Initialize scaling system
        self._initialize_default_scaling_rules()
        self._initialize_resource_monitoring()
    
    def _initialize_default_scaling_rules(self):
        """Initialize default auto-scaling rules"""
        
        default_rules = [
            # CPU scaling rules
            ScalingRule(
                id="cpu_scale_up",
                name="CPU Scale Up Rule",
                resource_type=ResourceType.CPU,
                trigger_type=ScalingTrigger.THRESHOLD_BASED,
                scale_up_threshold=75.0,
                scale_down_threshold=40.0,
                cooldown_minutes=10,
                min_capacity=1.0,
                max_capacity=8.0,
                scaling_factor=1.5,
                priority=1,
                conditions={"sustained_minutes": 5}
            ),
            
            # Memory scaling rules  
            ScalingRule(
                id="memory_scale_up",
                name="Memory Scale Up Rule",
                resource_type=ResourceType.MEMORY,
                trigger_type=ScalingTrigger.THRESHOLD_BASED,
                scale_up_threshold=80.0,
                scale_down_threshold=50.0,
                cooldown_minutes=15,
                min_capacity=512.0,  # MB
                max_capacity=4096.0,  # MB
                scaling_factor=1.4,
                priority=2
            ),
            
            # Database connection scaling
            ScalingRule(
                id="db_connections_scale",
                name="Database Connections Scaling",
                resource_type=ResourceType.DATABASE_CONNECTIONS,
                trigger_type=ScalingTrigger.THRESHOLD_BASED,
                scale_up_threshold=85.0,
                scale_down_threshold=30.0,
                cooldown_minutes=20,
                min_capacity=10.0,
                max_capacity=100.0,
                scaling_factor=1.3,
                priority=3
            ),
            
            # Predictive scaling rule
            ScalingRule(
                id="predictive_scale",
                name="Predictive Scaling Rule",
                resource_type=ResourceType.CPU,
                trigger_type=ScalingTrigger.PREDICTIVE,
                scale_up_threshold=70.0,  # Lower threshold for predictive
                scale_down_threshold=35.0,
                cooldown_minutes=30,
                min_capacity=1.0,
                max_capacity=8.0,
                scaling_factor=1.2,
                priority=4,
                conditions={"forecast_confidence": 0.7}
            ),
            
            # Emergency scaling
            ScalingRule(
                id="emergency_scale",
                name="Emergency Scaling Rule", 
                resource_type=ResourceType.CPU,
                trigger_type=ScalingTrigger.EMERGENCY,
                scale_up_threshold=95.0,
                scale_down_threshold=0.0,  # Never scale down in emergency
                cooldown_minutes=5,
                min_capacity=1.0,
                max_capacity=16.0,
                scaling_factor=2.0,
                priority=0  # Highest priority
            )
        ]
        
        for rule in default_rules:
            self.scaling_rules[rule.id] = rule
        
        logger.info(f"✅ Initialized {len(default_rules)} default scaling rules")
    
    def _initialize_resource_monitoring(self):
        """Initialize resource monitoring baselines"""
        
        # Initialize baseline metrics for different resource types
        baseline_metrics = {
            ResourceType.CPU: ResourceMetrics(
                resource_type=ResourceType.CPU,
                current_usage=2.0,
                capacity=4.0,
                utilization_percentage=50.0,
                trend_direction="stable",
                peak_usage_24h=3.2,
                avg_usage_7d=2.1,
                timestamp=datetime.now()
            ),
            ResourceType.MEMORY: ResourceMetrics(
                resource_type=ResourceType.MEMORY,
                current_usage=1024.0,  # MB
                capacity=2048.0,
                utilization_percentage=50.0,
                trend_direction="stable",
                peak_usage_24h=1536.0,
                avg_usage_7d=1100.0,
                timestamp=datetime.now()
            ),
            ResourceType.DATABASE_CONNECTIONS: ResourceMetrics(
                resource_type=ResourceType.DATABASE_CONNECTIONS,
                current_usage=15.0,
                capacity=50.0,
                utilization_percentage=30.0,
                trend_direction="stable",
                peak_usage_24h=25.0,
                avg_usage_7d=18.0,
                timestamp=datetime.now()
            )
        }
        
        self.resource_metrics = baseline_metrics
        logger.info("✅ Resource monitoring baselines initialized")
    
    async def collect_resource_metrics(self) -> Dict[str, Any]:
        """Collect current resource utilization metrics"""
        try:
            updated_metrics = {}
            
            # Simulate real resource collection (in production, integrate with monitoring systems)
            current_time = datetime.now()
            
            # Update CPU metrics
            cpu_metrics = await self._collect_cpu_metrics()
            updated_metrics[ResourceType.CPU] = cpu_metrics
            
            # Update memory metrics
            memory_metrics = await self._collect_memory_metrics()
            updated_metrics[ResourceType.MEMORY] = memory_metrics
            
            # Update database metrics
            db_metrics = await self._collect_database_metrics()
            updated_metrics[ResourceType.DATABASE_CONNECTIONS] = db_metrics
            
            # Update API rate limit metrics
            api_metrics = await self._collect_api_metrics()
            updated_metrics[ResourceType.API_RATE_LIMITS] = api_metrics
            
            # Store updated metrics
            self.resource_metrics.update(updated_metrics)
            
            return {
                "status": "success",
                "metrics_collected": len(updated_metrics),
                "collection_timestamp": current_time.isoformat(),
                "resource_statuses": {
                    resource.name: metrics.status.value 
                    for resource, metrics in updated_metrics.items()
                },
                "utilization_summary": {
                    resource.name: f"{metrics.utilization_percentage:.1f}%"
                    for resource, metrics in updated_metrics.items()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error collecting resource metrics: {e}")
            return {"error": str(e)}
    
    async def _collect_cpu_metrics(self) -> ResourceMetrics:
        """Collect CPU utilization metrics"""
        try:
            # Simulate CPU metrics (integrate with system monitoring)
            import random
            random.seed(int(datetime.now().timestamp()) % 1000)
            
            # Base usage with some variation
            current_usage = 2.0 + random.uniform(-0.5, 1.0)
            capacity = 4.0
            utilization = (current_usage / capacity) * 100
            
            # Simulate trend based on recent activity
            if self.metrics:
                # If we have user activity, simulate higher CPU usage
                recent_activity = random.uniform(0.8, 1.2)  # Activity factor
                current_usage *= recent_activity
                utilization = min(100, (current_usage / capacity) * 100)
            
            return ResourceMetrics(
                resource_type=ResourceType.CPU,
                current_usage=current_usage,
                capacity=capacity,
                utilization_percentage=utilization,
                trend_direction="increasing" if utilization > 60 else "stable",
                peak_usage_24h=current_usage * 1.3,
                avg_usage_7d=current_usage * 0.8,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {e}")
            raise
    
    async def _collect_memory_metrics(self) -> ResourceMetrics:
        """Collect memory utilization metrics"""
        try:
            import random
            random.seed(int(datetime.now().timestamp()) % 1000 + 1)
            
            current_usage = 1024 + random.uniform(-200, 400)  # MB
            capacity = 2048.0
            utilization = (current_usage / capacity) * 100
            
            return ResourceMetrics(
                resource_type=ResourceType.MEMORY,
                current_usage=current_usage,
                capacity=capacity,
                utilization_percentage=utilization,
                trend_direction="stable",
                peak_usage_24h=current_usage * 1.2,
                avg_usage_7d=current_usage * 0.9,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")
            raise
    
    async def _collect_database_metrics(self) -> ResourceMetrics:
        """Collect database connection metrics"""
        try:
            # Simulate based on potential user activity
            base_connections = 15
            
            # Simulate connection usage
            import random
            random.seed(int(datetime.now().timestamp()) % 1000 + 2)
            
            current_usage = base_connections + random.uniform(-5, 15)
            capacity = 50.0
            utilization = (current_usage / capacity) * 100
            
            return ResourceMetrics(
                resource_type=ResourceType.DATABASE_CONNECTIONS,
                current_usage=max(1, current_usage),
                capacity=capacity,
                utilization_percentage=utilization,
                trend_direction="stable",
                peak_usage_24h=current_usage * 1.4,
                avg_usage_7d=current_usage * 0.85,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            raise
    
    async def _collect_api_metrics(self) -> ResourceMetrics:
        """Collect API rate limit metrics"""
        try:
            import random
            random.seed(int(datetime.now().timestamp()) % 1000 + 3)
            
            # Simulate API usage
            current_usage = random.uniform(100, 800)  # requests per minute
            capacity = 1000.0
            utilization = (current_usage / capacity) * 100
            
            return ResourceMetrics(
                resource_type=ResourceType.API_RATE_LIMITS,
                current_usage=current_usage,
                capacity=capacity,
                utilization_percentage=utilization,
                trend_direction="stable",
                peak_usage_24h=capacity * 0.9,
                avg_usage_7d=current_usage * 0.7,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error collecting API metrics: {e}")
            raise
    
    async def evaluate_scaling_decisions(self) -> Dict[str, Any]:
        """Evaluate current state and determine scaling actions needed"""
        try:
            # Collect latest metrics
            await self.collect_resource_metrics()
            
            scaling_decisions = []
            
            # Evaluate each scaling rule
            for rule_id, rule in self.scaling_rules.items():
                if not rule.enabled:
                    continue
                
                resource_metrics = self.resource_metrics.get(rule.resource_type)
                if not resource_metrics:
                    continue
                
                decision = await self._evaluate_single_rule(rule, resource_metrics)
                if decision:
                    scaling_decisions.append(decision)
            
            # Sort by priority (lower number = higher priority)
            scaling_decisions.sort(key=lambda x: x.get("priority", 999))
            
            # Execute highest priority actions
            executed_actions = []
            for decision in scaling_decisions[:3]:  # Execute top 3 actions
                action = await self._create_scaling_action(decision)
                if action:
                    executed_actions.append(action)
            
            return {
                "evaluation_timestamp": datetime.now().isoformat(),
                "rules_evaluated": len(self.scaling_rules),
                "scaling_decisions": len(scaling_decisions),
                "actions_executed": len(executed_actions),
                "decisions": scaling_decisions,
                "executed_actions": [asdict(action) for action in executed_actions],
                "resource_status": {
                    resource.name: metrics.status.value
                    for resource, metrics in self.resource_metrics.items()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error evaluating scaling decisions: {e}")
            return {"error": str(e)}
    
    async def _evaluate_single_rule(self, rule: ScalingRule, metrics: ResourceMetrics) -> Optional[Dict[str, Any]]:
        """Evaluate a single scaling rule against current metrics"""
        try:
            current_utilization = metrics.utilization_percentage
            
            # Check cooldown period
            if not self._is_cooldown_expired(rule):
                return None
            
            # Determine scaling direction
            scaling_direction = None
            confidence_score = 0.8
            
            if rule.trigger_type == ScalingTrigger.THRESHOLD_BASED:
                if current_utilization >= rule.scale_up_threshold:
                    scaling_direction = ScalingDirection.UP
                    confidence_score = min(1.0, (current_utilization - rule.scale_up_threshold) / 20.0 + 0.6)
                elif current_utilization <= rule.scale_down_threshold:
                    scaling_direction = ScalingDirection.DOWN
                    confidence_score = min(1.0, (rule.scale_down_threshold - current_utilization) / 30.0 + 0.5)
            
            elif rule.trigger_type == ScalingTrigger.PREDICTIVE:
                # Use predictive system if available
                if self.predictive:
                    prediction = await self._get_capacity_prediction(rule.resource_type)
                    if prediction and prediction.confidence_score >= rule.conditions.get("forecast_confidence", 0.7):
                        if prediction.predicted_peak_usage >= rule.scale_up_threshold:
                            scaling_direction = ScalingDirection.UP
                            confidence_score = prediction.confidence_score
            
            elif rule.trigger_type == ScalingTrigger.EMERGENCY:
                if current_utilization >= rule.scale_up_threshold:
                    scaling_direction = ScalingDirection.UP
                    confidence_score = 1.0  # High confidence for emergency scaling
            
            if scaling_direction is None:
                return None
            
            # Calculate target capacity
            current_capacity = metrics.capacity
            if scaling_direction == ScalingDirection.UP:
                target_capacity = min(rule.max_capacity, current_capacity * rule.scaling_factor)
            else:
                target_capacity = max(rule.min_capacity, current_capacity / rule.scaling_factor)
            
            # Estimate cost and performance impact
            cost_impact = self._estimate_cost_impact(rule.resource_type, current_capacity, target_capacity)
            performance_impact = self._estimate_performance_impact(scaling_direction, rule.scaling_factor)
            
            return {
                "rule_id": rule.id,
                "resource_type": rule.resource_type.value,
                "direction": scaling_direction.value,
                "trigger": rule.trigger_type.value,
                "current_capacity": current_capacity,
                "target_capacity": target_capacity,
                "current_utilization": current_utilization,
                "threshold_breached": rule.scale_up_threshold if scaling_direction == ScalingDirection.UP else rule.scale_down_threshold,
                "confidence_score": confidence_score,
                "priority": rule.priority,
                "estimated_cost_impact": cost_impact,
                "estimated_performance_impact": performance_impact,
                "reason": self._generate_scaling_reason(rule, metrics, scaling_direction)
            }
            
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.id}: {e}")
            return None
    
    def _is_cooldown_expired(self, rule: ScalingRule) -> bool:
        """Check if cooldown period has expired for a scaling rule"""
        # Find last action for this rule
        last_action = None
        for action in reversed(self.scaling_actions):
            if action.rule_id == rule.id:
                last_action = action
                break
        
        if not last_action:
            return True  # No previous action, cooldown is expired
        
        cooldown_period = timedelta(minutes=rule.cooldown_minutes)
        return (datetime.now() - last_action.created_at) >= cooldown_period
    
    async def _get_capacity_prediction(self, resource_type: ResourceType) -> Optional[CapacityForecast]:
        """Get capacity prediction for resource type"""
        try:
            if not self.predictive:
                return None
            
            # This would integrate with the predictive analytics system
            # For now, create a simple forecast
            current_metrics = self.resource_metrics.get(resource_type)
            if not current_metrics:
                return None
            
            # Simple prediction based on current trends
            predicted_peak = current_metrics.peak_usage_24h * 1.1
            predicted_avg = current_metrics.avg_usage_7d * 1.05
            
            return CapacityForecast(
                resource_type=resource_type,
                forecast_horizon_hours=24,
                predicted_peak_usage=predicted_peak,
                predicted_avg_usage=predicted_avg,
                confidence_score=0.75,
                recommended_capacity=predicted_peak * 1.2,  # 20% buffer
                cost_optimization_opportunities=[],
                risk_factors=[],
                generated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting capacity prediction: {e}")
            return None
    
    def _estimate_cost_impact(self, resource_type: ResourceType, current_capacity: float, target_capacity: float) -> float:
        """Estimate cost impact of scaling action"""
        try:
            # Cost per unit for different resources (simplified)
            cost_per_unit = {
                ResourceType.CPU: 0.10,  # $ per core per hour
                ResourceType.MEMORY: 0.05,  # $ per GB per hour
                ResourceType.DATABASE_CONNECTIONS: 0.02,  # $ per connection per hour
                ResourceType.API_RATE_LIMITS: 0.001,  # $ per request
                ResourceType.STORAGE: 0.01,  # $ per GB per hour
                ResourceType.BANDWIDTH: 0.05   # $ per GB
            }
            
            unit_cost = cost_per_unit.get(resource_type, 0.05)
            capacity_change = target_capacity - current_capacity
            
            # Hourly cost impact
            hourly_cost_change = capacity_change * unit_cost
            
            # Daily cost impact
            return hourly_cost_change * 24
            
        except Exception as e:
            logger.error(f"Error estimating cost impact: {e}")
            return 0.0
    
    def _estimate_performance_impact(self, direction: ScalingDirection, scaling_factor: float) -> float:
        """Estimate performance impact of scaling action"""
        try:
            if direction == ScalingDirection.UP:
                # Scaling up improves performance
                return (scaling_factor - 1.0) * 100  # Percentage improvement
            elif direction == ScalingDirection.DOWN:
                # Scaling down may reduce performance
                return -((scaling_factor - 1.0) * 50)  # Smaller negative impact
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error estimating performance impact: {e}")
            return 0.0
    
    def _generate_scaling_reason(self, rule: ScalingRule, metrics: ResourceMetrics, direction: ScalingDirection) -> str:
        """Generate human-readable reason for scaling action"""
        try:
            resource_name = rule.resource_type.value.replace('_', ' ').title()
            utilization = metrics.utilization_percentage
            
            if direction == ScalingDirection.UP:
                threshold = rule.scale_up_threshold
                return f"{resource_name} utilization at {utilization:.1f}% exceeds scale-up threshold of {threshold}%"
            elif direction == ScalingDirection.DOWN:
                threshold = rule.scale_down_threshold
                return f"{resource_name} utilization at {utilization:.1f}% is below scale-down threshold of {threshold}%"
            else:
                return f"{resource_name} scaling evaluation completed"
                
        except Exception as e:
            logger.error(f"Error generating scaling reason: {e}")
            return "Scaling action triggered by rule evaluation"
    
    async def _create_scaling_action(self, decision: Dict[str, Any]) -> Optional[ScalingAction]:
        """Create and execute a scaling action based on decision"""
        try:
            action = ScalingAction(
                id=str(uuid.uuid4()),
                rule_id=decision["rule_id"],
                resource_type=ResourceType(decision["resource_type"]),
                direction=ScalingDirection(decision["direction"]),
                trigger=ScalingTrigger(decision["trigger"]),
                current_capacity=decision["current_capacity"],
                target_capacity=decision["target_capacity"],
                scaling_factor=decision["target_capacity"] / decision["current_capacity"],
                reason=decision["reason"],
                confidence_score=decision["confidence_score"],
                estimated_cost_impact=decision["estimated_cost_impact"],
                estimated_performance_impact=decision["estimated_performance_impact"],
                created_at=datetime.now()
            )
            
            # Execute the scaling action (simulation)
            execution_result = await self._execute_scaling_action(action)
            action.execution_result = execution_result
            action.executed_at = datetime.now()
            action.status = "completed" if execution_result.get("success") else "failed"
            
            # Store the action
            self.scaling_actions.append(action)
            
            # Update capacity in metrics (simulate the scaling effect)
            if execution_result.get("success"):
                await self._update_resource_capacity(action.resource_type, action.target_capacity)
            
            logger.info(f"✅ Scaling action executed: {action.direction.value} {action.resource_type.value} from {action.current_capacity} to {action.target_capacity}")
            
            return action
            
        except Exception as e:
            logger.error(f"❌ Error creating scaling action: {e}")
            return None
    
    async def _execute_scaling_action(self, action: ScalingAction) -> Dict[str, Any]:
        """Execute the actual scaling action (simulation)"""
        try:
            # In a real system, this would:
            # - Call cloud provider APIs
            # - Update load balancer configurations
            # - Modify database connection pools
            # - Adjust rate limits
            # etc.
            
            # Simulate execution time
            await asyncio.sleep(0.1)
            
            # Simulate success/failure
            import random
            success_rate = 0.95  # 95% success rate
            success = random.random() < success_rate
            
            if success:
                return {
                    "success": True,
                    "execution_time_ms": 1500,
                    "new_capacity": action.target_capacity,
                    "confirmation": f"Successfully scaled {action.resource_type.value} to {action.target_capacity}"
                }
            else:
                return {
                    "success": False,
                    "error": "Scaling operation failed due to resource constraints",
                    "retry_recommended": True
                }
                
        except Exception as e:
            logger.error(f"Error executing scaling action: {e}")
            return {"success": False, "error": str(e)}
    
    async def _update_resource_capacity(self, resource_type: ResourceType, new_capacity: float):
        """Update resource capacity after successful scaling"""
        try:
            if resource_type in self.resource_metrics:
                metrics = self.resource_metrics[resource_type]
                old_capacity = metrics.capacity
                metrics.capacity = new_capacity
                metrics.utilization_percentage = (metrics.current_usage / new_capacity) * 100
                metrics.timestamp = datetime.now()
                
                # Update status based on new utilization
                if metrics.utilization_percentage > 90:
                    metrics.status = ResourceStatus.CRITICAL
                elif metrics.utilization_percentage > 75:
                    metrics.status = ResourceStatus.OVER_UTILIZED
                elif metrics.utilization_percentage < 30:
                    metrics.status = ResourceStatus.UNDER_UTILIZED
                else:
                    metrics.status = ResourceStatus.OPTIMAL
                
                logger.info(f"📊 Updated {resource_type.value} capacity from {old_capacity} to {new_capacity}")
                
        except Exception as e:
            logger.error(f"Error updating resource capacity: {e}")
    
    async def generate_optimization_recommendations(self) -> Dict[str, Any]:
        """Generate resource optimization recommendations"""
        try:
            recommendations = []
            
            # Analyze current resource utilization patterns
            for resource_type, metrics in self.resource_metrics.items():
                
                # Rightsizing recommendations
                if metrics.status == ResourceStatus.UNDER_UTILIZED:
                    recommendations.append(ResourceOptimizationRecommendation(
                        id=str(uuid.uuid4()),
                        title=f"Rightsize {resource_type.value.replace('_', ' ').title()}",
                        description=f"Current utilization is only {metrics.utilization_percentage:.1f}%, suggesting over-provisioning",
                        resource_type=resource_type,
                        optimization_type="rightsizing",
                        current_state={"capacity": metrics.capacity, "utilization": metrics.utilization_percentage},
                        recommended_state={"capacity": metrics.capacity * 0.7, "expected_utilization": metrics.utilization_percentage * 1.43},
                        expected_savings={"cost_reduction_percent": 30.0, "performance_impact": -5.0},
                        implementation_complexity="low",
                        risk_level="low",
                        prerequisites=["Monitor for 24h after change", "Have rollback plan ready"],
                        created_at=datetime.now()
                    ))
                
                # Performance optimization recommendations
                elif metrics.status == ResourceStatus.OVER_UTILIZED:
                    recommendations.append(ResourceOptimizationRecommendation(
                        id=str(uuid.uuid4()),
                        title=f"Scale Up {resource_type.value.replace('_', ' ').title()}",
                        description=f"High utilization of {metrics.utilization_percentage:.1f}% may impact performance",
                        resource_type=resource_type,
                        optimization_type="performance",
                        current_state={"capacity": metrics.capacity, "utilization": metrics.utilization_percentage},
                        recommended_state={"capacity": metrics.capacity * 1.3, "expected_utilization": metrics.utilization_percentage * 0.77},
                        expected_savings={"performance_improvement": 25.0, "cost_increase_percent": 30.0},
                        implementation_complexity="low",
                        risk_level="low",
                        prerequisites=["Budget approval for increased capacity"],
                        created_at=datetime.now()
                    ))
            
            # Schedule-based optimization
            recommendations.append(ResourceOptimizationRecommendation(
                id=str(uuid.uuid4()),
                title="Implement Schedule-Based Scaling",
                description="Set up predictive scaling based on usage patterns",
                resource_type=ResourceType.CPU,
                optimization_type="scheduling",
                current_state={"scaling_type": "reactive"},
                recommended_state={"scaling_type": "predictive", "lead_time_minutes": 15},
                expected_savings={"cost_reduction_percent": 15.0, "performance_improvement": 20.0},
                implementation_complexity="medium",
                risk_level="medium",
                prerequisites=["Historical data analysis", "Predictive model training"],
                created_at=datetime.now()
            ))
            
            # Store recommendations
            self.optimization_recommendations.extend(recommendations)
            
            return {
                "recommendations_generated": len(recommendations),
                "recommendations": [asdict(rec) for rec in recommendations],
                "potential_savings": {
                    "total_cost_reduction": sum(rec.expected_savings.get("cost_reduction_percent", 0) for rec in recommendations),
                    "performance_improvements": [rec.expected_savings.get("performance_improvement", 0) for rec in recommendations if rec.expected_savings.get("performance_improvement", 0) > 0]
                },
                "generation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating optimization recommendations: {e}")
            return {"error": str(e)}
    
    async def get_scaling_status(self) -> Dict[str, Any]:
        """Get current auto-scaling system status"""
        try:
            # Calculate scaling statistics
            total_actions = len(self.scaling_actions)
            successful_actions = len([a for a in self.scaling_actions if a.status == "completed"])
            recent_actions = len([a for a in self.scaling_actions if a.created_at > datetime.now() - timedelta(hours=24)])
            
            success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 100
            
            # Active scaling rules
            active_rules = len([r for r in self.scaling_rules.values() if r.enabled])
            
            # Resource status summary
            resource_status_summary = {}
            for resource_type, metrics in self.resource_metrics.items():
                resource_status_summary[resource_type.value] = {
                    "utilization": f"{metrics.utilization_percentage:.1f}%",
                    "status": metrics.status.value,
                    "capacity": metrics.capacity,
                    "trend": metrics.trend_direction
                }
            
            # Cost impact summary
            total_cost_impact = sum(action.estimated_cost_impact for action in self.scaling_actions)
            
            return {
                "system_status": "operational",
                "scaling_rules": {
                    "total": len(self.scaling_rules),
                    "active": active_rules,
                    "disabled": len(self.scaling_rules) - active_rules
                },
                "scaling_actions": {
                    "total": total_actions,
                    "successful": successful_actions,
                    "success_rate": f"{success_rate:.1f}%",
                    "recent_24h": recent_actions
                },
                "resource_status": resource_status_summary,
                "optimization_recommendations": len(self.optimization_recommendations),
                "cost_impact_24h": f"${total_cost_impact:.2f}",
                "last_evaluation": max([a.created_at for a in self.scaling_actions]).isoformat() if self.scaling_actions else None,
                "system_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting scaling status: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    print("Auto-scaling System - Intelligent resource optimization and capacity management for Progress Method")