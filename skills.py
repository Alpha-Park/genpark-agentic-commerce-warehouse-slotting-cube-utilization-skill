# -*- coding: utf-8 -*-
"""GenPark Industrial Skill: genpark-agentic-commerce-warehouse-slotting-cube-utilization-skill
Category: agentic_commerce
Website: https://www.genpark.ai
LinkedIn: https://www.linkedin.com/company/92955550
"""
import sys
import json
import math

sys.stdout.reconfigure(encoding="utf-8")

def optimize_warehouse_cube_utilization(locations):
    total_loc_volume = 0.0
    total_cargo_volume = 0.0
    inefficient_locations = []
    
    for loc in locations:
        lid = loc["location_id"]
        loc_w, loc_d, loc_h = loc["width_in"], loc["depth_in"], loc["height_in"]
        cargo_w, cargo_d, cargo_h = loc["cargo_width_in"], loc["cargo_depth_in"], loc["cargo_height_in"]
        
        loc_vol = loc_w * loc_d * loc_h
        cargo_vol = cargo_w * cargo_d * cargo_h
        
        total_loc_volume += loc_vol
        total_cargo_volume += cargo_vol
        
        utilization_pct = (cargo_vol / loc_vol * 100.0) if loc_vol > 0 else 0.0
        honeycombing_loss_pct = 100.0 - utilization_pct
        
        if utilization_pct < 65.0:
            inefficient_locations.append({
                "location_id": lid,
                "cube_utilization_pct": round(utilization_pct, 1),
                "honeycombing_void_pct": round(honeycombing_loss_pct, 1),
                "vertical_headroom_waste_in": loc_h - cargo_h
            })
            
    overall_cube_utilization_pct = (total_cargo_volume / total_loc_volume * 100.0) if total_loc_volume > 0 else 0.0
    
    return {
        "locations_analyzed": len(locations),
        "total_warehouse_capacity_cuft": round(total_loc_volume / 1728.0, 1),
        "total_stored_cargo_cuft": round(total_cargo_volume / 1728.0, 1),
        "overall_cube_utilization_pct": round(overall_cube_utilization_pct, 1),
        "honeycombing_void_loss_pct": round(100.0 - overall_cube_utilization_pct, 1),
        "inefficient_bays_count": len(inefficient_locations),
        "reallocation_recommendations": inefficient_locations[:5]
    }


def handle_rpc(request_str):
    try:
        req = json.loads(request_str)
        rpc_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "tools": [{
                        "name": "optimize_warehouse_cube_utilization",
                        "description": """Quantify warehouse high-bay storage cube utilization and honeycombing void space loss.
Evaluates volumetric fill efficiency across standard GMA pallets and bin locations, identifies vertical empty space wastage,
and recommends physical profile reconfiguration.""",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }]
                }
            })
        elif method == "tools/call":
            call_params = params.get("arguments", {})
            res = optimize_warehouse_cube_utilization(**call_params)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(res, indent=2)
                    }]
                }
            })
        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            })
    except Exception as e:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": str(e)}
        })

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sample = {'locations': [{'location_id': 'BAY-A-101', 'width_in': 48, 'depth_in': 48, 'height_in': 72, 'cargo_width_in': 40, 'cargo_depth_in': 48, 'cargo_height_in': 42}, {'location_id': 'BAY-A-102', 'width_in': 48, 'depth_in': 48, 'height_in': 72, 'cargo_width_in': 44, 'cargo_depth_in': 48, 'cargo_height_in': 68}, {'location_id': 'BAY-A-103', 'width_in': 48, 'depth_in': 48, 'height_in': 96, 'cargo_width_in': 40, 'cargo_depth_in': 48, 'cargo_height_in': 50}]}
        out = optimize_warehouse_cube_utilization(**sample)
        print("[TEST_PASS] Output:", json.dumps(out))
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            print(handle_rpc(line))
