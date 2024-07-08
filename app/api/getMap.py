from quart import Blueprint, request, jsonify
from ..utils.gene import gene_map
import asyncio


getMap_bp = Blueprint('getMap', __name__)

@getMap_bp.route('/getMap', methods=['POST'])
async def getMap():
    data = await request.get_json()
    serial_number = data.get('serial_number')
    size = tuple(data.get('size', [20, 20]))  # 默认大小为(20, 20)
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, gene_map, serial_number, size)

    response = {
        "result_map": result[0],
        "path_map": result[1],
        "middle_wall": result[2]
    }

    return jsonify(response)