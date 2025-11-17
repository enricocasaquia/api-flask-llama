class MetricsModel:
    total_prompts = 0
    total_tokens = 0
    total_errors = 0
    total_time = 0
    total_cpu_percent = 0
    total_gpu_percent = 0
    total_gpu_mb = 0
    total_ram_mb = 0
    gpu_available = True
    last_requests = []

    @classmethod
    def capture_metrics(cls, tokens, inference_time, cpu_percent, gpu_data, ram_mb, status_code):
        cls.total_prompts += 1
        cls.total_tokens += tokens
        cls.total_time += inference_time
        cls.total_cpu_percent += cpu_percent
        cls.total_ram_mb += ram_mb
        if gpu_data is not None:
            cls.total_gpu_percent += gpu_data["percent"]
            cls.total_gpu_mb += gpu_data["mb"]
        
        cls.last_requests.append({
            "status": status_code,
            "tokens": tokens,
            "time": inference_time,
            "cpu_percent": cpu_percent,
            "ram_mb": ram_mb,
            "gpu": gpu_data
        })
        
        if len(cls.last_requests) > 20:
            cls.last_requests.pop(0)
