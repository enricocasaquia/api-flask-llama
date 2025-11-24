from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models.metrics import MetricsModel

class Metrics(Resource):
    @jwt_required()
    def get(self):
        """
        Returns system metrics
        ---
        tags:
          - Metrics
        responses:
          200:
            description: Metrics data
          500:
            description: Error while retrieving metrics
        """
        try:
            if MetricsModel.total_prompts > 0:
                avg_cpu = MetricsModel.total_cpu_percent / MetricsModel.total_prompts
                avg_ram = MetricsModel.total_ram_mb / MetricsModel.total_prompts
                avg_gpu_load = (MetricsModel.total_gpu_percent / MetricsModel.total_prompts
                                if MetricsModel.total_gpu_percent > 0 else 0)
                avg_gpu_mem = (MetricsModel.total_gpu_mb / MetricsModel.total_prompts
                            if MetricsModel.total_gpu_mb > 0 else 0)
            else:
                avg_cpu = avg_ram = avg_gpu_load = avg_gpu_mem = 0

            return {
                "total_prompts": MetricsModel.total_prompts,
                "total_tokens": MetricsModel.total_tokens,
                "avg_inference_time": (
                    MetricsModel.total_time / MetricsModel.total_prompts
                    if MetricsModel.total_prompts > 0 else 0
                ),
                "avg_cpu_percent": avg_cpu,
                "avg_ram_used_mb": avg_ram,
                "avg_gpu_load_percent": avg_gpu_load,
                "avg_gpu_mem_mb": avg_gpu_mem,
                "last_requests": MetricsModel.last_requests[-20:]
            }, 200
        except Exception as e:
            return {
                'message': f'Error while retrieving metrics.'
            }, 500