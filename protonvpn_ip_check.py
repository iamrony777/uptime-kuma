import json
import os

import aiofiles
from httpx import AsyncClient

LOGICALS_URL = 'https://api.protonvpn.ch/vpn/logicals'
TOKEN = os.getenv('IPINFO_TOKEN')


async def get_ip_list() -> list:
    """Extract ExitIp from protonservers.json"""
    proton_servers = []
    try:
        async with aiofiles.open('./protonservers.json', 'r', encoding='UTF-8') as read_servers:
            data = json.loads(await read_servers.read())
            for logical in data['LogicalServers']:
                for servers in logical['Servers']:
                    proton_servers.append(servers['ExitIP'])
        return proton_servers
    except Exception:
        return None


async def check_local_data() -> None:
    """Check if local data is up to date"""
    if os.path.isfile('./protonservers.json'):
        return
    async with aiofiles.open('./protonservers.json', 'w', encoding='UTF-8') as write_servers:
        async with AsyncClient(timeout=30) as client:
            try:
                await write_servers.write(json.dumps((await client.get(LOGICALS_URL)).json()))
                return
            except Exception:
                return


async def check_current_ip() -> str:
    """Check current ip"""
    async with AsyncClient(base_url='https://ipinfo.io', headers={'Accept': 'application/json', 'Authorization': f'Bearer {TOKEN}'}, timeout=30) as client:
        return (await client.get('/')).json()['ip']


async def main() -> None:
    """Main function"""
    while True:
        await check_local_data()
        proton_servers = await get_ip_list()
        if proton_servers is not None:
            my_ip = await check_current_ip()
            if my_ip in proton_servers:
                print(f'You are connected to ProtonVPN [{my_ip}]')
                exit(0)
            print(f'You are not connected to ProtonVPN [{my_ip}]')
            await asyncio.sleep(120)
        print('Connection Error')
        os.remove('protonservers.json')
        await asyncio.sleep(120)
        continue


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
