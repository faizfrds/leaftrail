import time
import functools

# Mock data for demonstration (In production, query BigQuery or Carbon Footprint API)
REGION_CFE_DATA = {
    "us-central1": 0.87,  # Iowa: 87% Carbon Free
    "europe-north2": 1.00, # Stockholm: 100% Carbon Free
    "us-east1": 0.52,      # South Carolina: 52% Carbon Free
}

# Energy intensity per 1k tokens (Estimated in Wh) according to Google's reports
MODEL_INTENSITY = 0.24

# Power Usage Effectiveness (PUE) is a measure of how much energy is used by the data center infrastructure compared to the IT equipment.
PUE = 1.1 #Gemini models live in Google's data centers which can be baselined as 1.1, according to Google's reports

def leaftrail(func):
    """
    Leaftrail Decorator: Intercepts Gemini API calls to calculate 
    CO2, Water, and Energy footprint.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Capture metadata before execution
        model_name = kwargs.get('model', 'unknown-model')
        # In a real GCP environment, this can be pulled from environment variables
        region = "us-central1" 
        
        print(f"🟢 [Leaftrail] Monitoring call to {model_name} in {region}...")
        
        start_time = time.perf_counter()
        
        # 2. Execute the actual LLM call
        response = func(*args, **kwargs)
        
        end_time = time.perf_counter()
        latency = end_time - start_time

        # 3. Extract Token Usage from Gemini Response
        # The new SDK provides usage_metadata directly
        usage = response.usage_metadata
        total_tokens = usage.total_token_count
        
        # 4. Impact Engine Logic
        # Energy (Wh) = (Intensity * Tokens/1000) * PUE
        energy_used = (MODEL_INTENSITY * (total_tokens / 1000)) * PUE  # 1.1 PUE
        
        # Carbon calculation (gCO2e)
        # We assume a baseline grid intensity of 400g/kWh if not specified
        grid_intensity_kwh = 400 
        cfe_factor = REGION_CFE_DATA.get(region, 0.5)
        carbon_emitted = (energy_used / 1000) * grid_intensity_kwh * (1 - cfe_factor)
        
        # Water calculation (mL)
        water_used = energy_used * 0.26 # Based on Google's 0.26mL/Wh average

        # 5. Log the "Thinking" process to the console
        print(f"🔍 [Leaftrail Audit]")
        print(f"   | Tokens: {total_tokens} | Latency: {latency:.2f}s")
        print(f"   | Energy: {energy_used:.4f} Wh")
        print(f"   | Water:  {water_used:.4f} mL")
        print(f"   | Net CO2: {carbon_emitted:.4f} gCO2e")
        
        if carbon_emitted < 0.01:
            print("   ✨ Efficiency Badge Earned: Ultra-Low Carbon call!")

        return response

    return wrapper

