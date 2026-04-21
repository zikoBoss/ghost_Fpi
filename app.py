import requests, os, psutil, sys, jwt, pickle, json, binascii, time, urllib3, base64, datetime, re, socket, threading
import asyncio
import random
from protobuf_decoder.protobuf_decoder import Parser
from byte import *
from byte import xSendTeamMsg
from byte import Auth_Chat
from xHeaders import *
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from flask import Flask, request, jsonify
import tempfile
from google_play_scraper import app as google_play_app

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  

app = Flask(__name__)

connected_clients = {}
connected_clients_lock = threading.Lock()

current_server_domain = None
current_release_version = None
current_play_version = None
current_payload_template = None

def EnV(n):
    if n < 0:
        raise ValueError("non-negative only")
    o = []
    while True:
        b = n & 0x7F
        n >>= 7
        o.append(b | 0x80 if n else b)
        if not n:
            break
    return bytes(o)

def VFi(f, v):
    return EnV((f << 3) | 0) + EnV(v)

def LFi(f, v):
    b = v.encode() if isinstance(v, str) else v
    return EnV((f << 3) | 2) + EnV(len(b)) + b

def TerGeT(d):
    p = bytearray()
    for k, v in d.items():
        f = int(k)
        if isinstance(v, dict):
            p += LFi(f, TerGeT(v))
        elif isinstance(v, int):
            p += VFi(f, v)
        elif isinstance(v, (str, bytes)):
            p += LFi(f, v)
    return bytes(p)

def fetch_latest_data():
    global current_server_domain, current_release_version, current_play_version, current_payload_template
    
    result = google_play_app('com.dts.freefireth', lang="fr", country='fr')
    current_play_version = result['version']
    
    r = requests.get(f'https://bdversion.ggbluefox.com/live/ver.php?version={current_play_version}&lang=ar&device=android&channel=android&appstore=googleplay&region=ME&whitelist_version=1.3.0&whitelist_sp_version=1.0.0&device_name=google%20G011A&device_CPU=ARMv7%20VFPv3%20NEON%20VMH&device_GPU=Adreno%20(TM)%20640&device_mem=1993', timeout=30, verify=False).json()
    
    server_url = r['server_url']
    full_domain = server_url.replace('https://', '').replace('http://', '').split('/')[0]
    domain_parts = full_domain.split('.')
    current_server_domain = '.'.join(domain_parts[-2:])
    current_release_version = r['latest_release_version']
    
    fields = {
        3: "2025-11-26 01:51:28",
        4: "free fire",
        5: 1,
        7: current_play_version,
        8: "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)",
        9: "Handheld",
        10: "MTN/Spacetel",
        11: "WIFI",
        12: 1280,
        13: 720,
        14: "240",
        15: "x86-64 SSE3 SSE4.1 SSE4.2 AVX AVX2 | 2400 | 4",
        16: 3942,
        17: "Adreno (TM) 640",
        18: "OpenGL ES 3.2",
        19: "Google|625f716f-91a7-495b-9f16-08fe9d3c6533",
        20: "176.28.139.185",
        21: "ar",
        22: "4306245793de86da425a52caadf21eed",
        23: "4",
        24: "Handheld",
        25: "OnePlus A5010",
        29: "c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94",
        30: 1,
        41: "MTN/Spacetel",
        42: "WIFI",
        57: "1ac4b80ecf0478a44203bf8fac6120f5",
        60: 46901,
        61: 32794,
        62: 2479,
        63: 900,
        64: 34727,
        65: 46901,
        66: 34727,
        67: 46901,
        70: 4,
        73: 1,
        74: "/data/app/com.dts.freefireth-fpXCSphIV6dKC7jL-WOyRA==/lib/arm",
        76: 1,
        77: "e62ab9354d8fb5fb081db338acb33491|/data/app/com.dts.freefireth-fpXCSphIV6dKC7jL-WOyRA==/base.apk",
        78: 6,
        79: 1,
        81: "32",
        83: "2019119026",
        85: 3,
        86: "OpenGLES2",
        87: 255,
        88: 4,
        92: 16190,
        93: "3rd_party",
        94: "KqsHT8W93GdcG3ZozENfFwVHtm7qq1eRUNaIDNgRobozIBtLOiYCc4Y6zvvpcICxzQF2sOE4cbytwLs4xZbRnpRMpmWRQKmeO5vcs8nQYBhwqH7K",
        95: 111207,
        97: 1,
        98: 1,
        99: "4",
        100: "4",
        102: "\u0013R\u0011FP\u000eY\u0003IQ\u000eF\t\u0000\u0011XC9_\u0000[Q\u000fh[V\na\u0007Wm\u000f\u0003f"
    }
    
    current_payload_template = TerGeT(fields)
    
    print(f"تم جلب البيانات: Domain={current_server_domain}, Release={current_release_version}, Version={current_play_version}")
    
    return True

def generate_random_color():
    color_list = [
        "[00FF00][b][c]", "[FFDD00][b][c]", "[3813F3][b][c]", "[FF0000][b][c]",
        "[0000FF][b][c]", "[FFA500][b][c]", "[DF07F8][b][c]", "[11EAFD][b][c]",
        "[DCE775][b][c]", "[A8E6CF][b][c]", "[7CB342][b][c]", "[FFB300][b][c]",
        "[90EE90][b][c]", "[FF4500][b][c]", "[FFD700][b][c]", "[32CD32][b][c]",
        "[87CEEB][b][c]", "[9370DB][b][c]", "[FF69B4][b][c]", "[8A2BE2][b][c]",
        "[00BFFF][b][c]", "[1E90FF][b][c]", "[20B2AA][b][c]", "[00FA9A][b][c]",
        "[008000][b][c]", "[FFFF00][b][c]", "[FF8C00][b][c]", "[DC143C][b][c]"
    ]
    return random.choice(color_list)

def get_random_accounts(count=1):
    with connected_clients_lock:
        if not connected_clients:
            return []
        available_clients = list(connected_clients.values())
        if count >= len(available_clients):
            return available_clients
        return random.sample(available_clients, count)

def AuTo_ResTartinG():
    # تعطيل إعادة التشغيل التلقائي في Railway
    pass

def ResTarT_BoT():
    # تعطيل إعادة التشغيل في Railway
    pass

def execute_blrx_command(client, teamcode, name, user_id, client_number):
    success = False
    try:
        
        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key and hasattr(client, 'iv') and client.iv:
            
            join_packet = JoinTeamCode(teamcode, client.key, client.iv)
            client.CliEnts2.send(join_packet)
            
            start_time = time.time()
            response_received = False
            idT = None
            sq = None
            
            while time.time() - start_time < 8:
                try:
                    if hasattr(client, 'DaTa2') and client.DaTa2 and len(client.DaTa2.hex()) > 30:
                        hex_data = client.DaTa2.hex()
                        if '0500' in hex_data[0:4]:
                            
                            try:
                                if "08" in hex_data:
                                    decoded_data = DeCode_PackEt(f'08{hex_data.split("08", 1)[1]}')
                                else:
                                    decoded_data = DeCode_PackEt(hex_data[10:])
                                
                                dT = json.loads(decoded_data)
                                
                                if "5" in dT and "data" in dT["5"]:
                                    team_data = dT["5"]["data"]
                                    
                                    if "31" in team_data and "data" in team_data["31"]:
                                        sq = team_data["31"]["data"]
                                        idT = team_data["1"]["data"]
                                        
                                        response_received = True
                                        break
                                    
                            except Exception as decode_error:
                                try:
                                    if len(hex_data) > 20:
                                        alternative_data = DeCode_PackEt(hex_data)
                                        if alternative_data:
                                            pass
                                except:
                                    pass
                    
                    time.sleep(0.1)
                    
                except Exception as loop_error:
                    time.sleep(0.1)
            
            if response_received and idT and sq:
                
                for i in range(99):
                    try:
                        client.CliEnts2.send(JoinTeamCode(teamcode, client.key, client.iv))
                        client.CliEnts2.send(GhostPakcet(idT, name, sq, client.key, client.iv))
                        time.sleep(0.1)
                        client.CliEnts2.send(ExitBot('000000', client.key, client.iv))
                        client.CliEnts2.send(GhostPakcet(idT, name, sq, client.key, client.iv))
                    except Exception as e:
                        break
                
                success = True
                
        else:
            pass
            
    except Exception as e:
        pass
    
    return success

def execute_ghost_command(client, teamcode, name, user_id, client_number, clients_list):
    success = False
    try:
        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key and hasattr(client, 'iv') and client.iv:
            
            join_packet = JoinTeamCode(teamcode, client.key, client.iv)
            client.CliEnts2.send(join_packet)
            
            start_time = time.time()
            response_received = False
            
            while time.time() - start_time < 8:
                try:
                    if hasattr(client, 'DaTa2') and client.DaTa2 and len(client.DaTa2.hex()) > 30:
                        hex_data = client.DaTa2.hex()
                        if '0500' in hex_data[0:4]:
                            
                            try:
                                if "08" in hex_data:
                                    decoded_data = DeCode_PackEt(f'08{hex_data.split("08", 1)[1]}')
                                else:
                                    decoded_data = DeCode_PackEt(hex_data[10:])
                                
                                dT = json.loads(decoded_data)
                                
                                if "5" in dT and "data" in dT["5"]:
                                    team_data = dT["5"]["data"]
                                    
                                    if "31" in team_data and "data" in team_data["31"]:
                                        sq = team_data["31"]["data"]
                                        idT = team_data["1"]["data"]
                                        
                                        client.CliEnts2.send(ExitBot('000000', client.key, client.iv))
                                        time.sleep(0.2)
                                        
                                        ghost_packet = GhostPakcet(idT, name, sq, client.key, client.iv)
                                        client.CliEnts2.send(ghost_packet)
                                        
                                        success = True
                                        response_received = True
                                        break
                                    
                            except Exception as decode_error:
                                try:
                                    if len(hex_data) > 20:
                                        alternative_data = DeCode_PackEt(hex_data)
                                        if alternative_data:
                                            pass
                                except:
                                    pass
                    
                    time.sleep(0.1)
                    
                except Exception as loop_error:
                    time.sleep(0.1)
            
            if not response_received:
                try:
                    ghost_packet_alt = GhostPakcet(teamcode, name, "1", client.key, client.iv)
                    client.CliEnts2.send(ghost_packet_alt)
                    time.sleep(0.5)
                    success = True
                except Exception as alt_error:
                    pass
            
        else:
            pass
            
    except Exception as e:
        pass
    
    return success


class FF_CLient():

    def __init__(self, id, password):
        self.id = id
        self.password = password
        self.key = None
        self.iv = None
        self.Get_FiNal_ToKen_0115()     
            
    def Connect_SerVer_OnLine(self , Token , tok , host , port , key , iv , host2 , port2):
            try:
                self.AutH_ToKen_0115 = tok    
                self.CliEnts2 = socket.create_connection((host2 , int(port2)))
                self.CliEnts2.send(bytes.fromhex(self.AutH_ToKen_0115))                  
            except:pass        
            while True:
                try:
                    self.DaTa2 = self.CliEnts2.recv(99999)
                    if '0500' in self.DaTa2.hex()[0:4] and len(self.DaTa2.hex()) > 30:	         	    	    
                            self.packet = json.loads(DeCode_PackEt(f'08{self.DaTa2.hex().split("08", 1)[1]}'))
                            self.AutH = self.packet['5']['data']['7']['data']
                    
                except:pass    	
                                                            
    def Connect_SerVer(self , Token , tok , host , port , key , iv , host2 , port2):
            self.AutH_ToKen_0115 = tok    
            self.CliEnts = socket.create_connection((host , int(port)))
            self.CliEnts.send(bytes.fromhex(self.AutH_ToKen_0115))  
            self.DaTa = self.CliEnts.recv(1024)          	        
            threading.Thread(target=self.Connect_SerVer_OnLine, args=(Token , tok , host , port , key , iv , host2 , port2)).start()
            self.Exemple = xMsGFixinG('12345678')
            
            self.key = key
            self.iv = iv
            
            with connected_clients_lock:
                connected_clients[self.id] = self
            
            while True:      
                try:
                    self.DaTa = self.CliEnts.recv(1024)   
                    if len(self.DaTa) == 0 or (hasattr(self, 'DaTa2') and len(self.DaTa2) == 0):	            		
                        try:            		    
                            self.CliEnts.close()
                            if hasattr(self, 'CliEnts2'):
                                self.CliEnts2.close()
                            self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)                    		                    
                        except:
                            try:
                                self.CliEnts.close()
                                if hasattr(self, 'CliEnts2'):
                                    self.CliEnts2.close()
                                self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)
                            except:
                                self.CliEnts.close()
                                if hasattr(self, 'CliEnts2'):
                                    self.CliEnts2.close()
                                ResTarT_BoT()	            
                           
                    if '1200' in self.DaTa.hex()[0:4] and 900 > len(self.DaTa.hex()) > 100:
                        if b"***" in self.DaTa:
                            self.DaTa = self.DaTa.replace(b"***",b"106")         
                        try:
                           self.BesTo_data = json.loads(DeCode_PackEt(self.DaTa.hex()[10:]))	       
                           self.input_msg = 'besto_love' if '8' in self.BesTo_data["5"]["data"] else self.BesTo_data["5"]["data"]["4"]["data"]
                        except: 
                            self.input_msg = None	   	 
                        self.DeCode_CliEnt_Uid = self.BesTo_data["5"]["data"]["1"]["data"]
                        self.CliEnt_Uid = EnC_Uid(self.DeCode_CliEnt_Uid , Tp = 'Uid')
                               
                    if 'Alli' in self.input_msg[:10]:
                        self.CliEnts.send(GenResponsMsg(f'''
[C][B][000000]━━━━━━━━━━━━ 

[C][B][000000]━━━━━━━━━━━━''', 2 , self.DeCode_CliEnt_Uid , self.DeCode_CliEnt_Uid , key , iv))
                        time.sleep(0.3)
                        self.CliEnts.close()
                        if hasattr(self, 'CliEnts2'):
                            self.CliEnts2.close()
                        self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)	                    	 	 
                                                                         

                except Exception as e:
                    try:
                        self.CliEnts.close()
                        if hasattr(self, 'CliEnts2'):
                            self.CliEnts2.close()
                    except:
                        pass
                    self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)
                                    
    def GeT_Key_Iv(self , serialized_data):
        my_message = xKEys.MyMessage()
        my_message.ParseFromString(serialized_data)
        timestamp , key , iv = my_message.field21 , my_message.field22 , my_message.field23
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        timestamp_seconds = timestamp_obj.seconds
        timestamp_nanos = timestamp_obj.nanos
        combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
        return combined_timestamp , key , iv    

    def Guest_GeneRaTe(self , uid , password):
        self.url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        self.headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close"
        }
        self.dataa = {
            "uid": f"{uid}",
            "password": f"{password}",
            "response_type": "token",
            "client_type": "2",
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_id": "100067"
        }
        
        try:
            if not uid or not password:
                print(f"❌ بيانات الحساب غير صالحة: {uid}")
                time.sleep(5)
                return self.Guest_GeneRaTe(uid, password)
                
            self.response = requests.post(self.url, headers=self.headers, data=self.dataa, timeout=30)
            
            if self.response.status_code != 200:
                print(f"❌ خطأ في الاستجابة: {self.response.status_code}")
                time.sleep(5)
                return self.Guest_GeneRaTe(uid, password)
                
            response_data = self.response.json()
            
            if 'access_token' not in response_data or 'open_id' not in response_data:
                print(f"❌ بيانات الاستجابة غير مكتملة: {response_data}")
                time.sleep(5)
                return self.Guest_GeneRaTe(uid, password)
            
            self.Access_ToKen = response_data['access_token']
            self.Access_Uid = response_data['open_id']
            
            print(f'✅ تم الحصول على التوكن للحساب: {uid}')
            time.sleep(0.5)

            return self.ToKen_GeneRaTe(self.Access_ToKen , self.Access_Uid)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ في الاتصال للحساب {uid}: {e}")
            time.sleep(5)
            return self.Guest_GeneRaTe(uid, password)
        except Exception as e:
            print(f"❌ خطأ غير متوقع للحساب {uid}: {e}")
            time.sleep(2)
            return self.Guest_GeneRaTe(uid, password)
                                        
    def GeT_LoGin_PorTs(self , JwT_ToKen , PayLoad):
        self.UrL = f'https://clientbp.{current_server_domain}/GetLoginData'
        self.HeadErs = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {JwT_ToKen}',
            'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': current_release_version,
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)',
            'Host': f'clientbp.{current_server_domain}',
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate, br'
        }       
        try:
            self.Res = requests.post(self.UrL, headers=self.HeadErs, data=PayLoad, verify=False, timeout=30)
            
            if self.Res.content:
                hex_content = self.Res.content.hex()
                try:
                    self.BesTo_data = json.loads(DeCode_PackEt(hex_content))  
                    address = self.BesTo_data['32']['data'] 
                    address2 = self.BesTo_data['14']['data']
                    
                    ip = address[:len(address) - 6] 
                    ip2 = address2[:len(address) - 6]
                    port = address[len(address) - 5:] 
                    port2 = address2[len(address2) - 5:]             
                    
                    return ip , port , ip2 , port2
                except Exception as e:
                    print(f"❌ خطأ في معالجة بيانات البورت: {e}")
                    return None, None, None, None
            else:
                print("❌ لا توجد بيانات في الاستجابة")
                return None, None, None, None
                
        except requests.RequestException as e:
            print(f"❌ خطأ في طلب البورتات: {e}")
            return None, None, None, None
        except Exception as e:
            print(f"❌ خطأ غير متوقع في طلب البورتات: {e}")
            return None, None, None, None
        
    def ToKen_GeneRaTe(self , Access_ToKen , Access_Uid):
        self.UrL = f'https://loginbp.{current_server_domain}/MajorLogin'
        self.HeadErs = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': current_release_version,
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': f'loginbp.{current_server_domain}',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'   
        }   
        
        self.dT = current_payload_template
        
        self.dT = self.dT.replace(b'2025-11-26 01:51:28', str(datetime.now())[:-7].encode())
        self.dT = self.dT.replace(b'4306245793de86da425a52caadf21eed', Access_Uid.encode())
        self.dT = self.dT.replace(b'c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94', Access_ToKen.encode())
        
        try:
            hex_data = self.dT.hex()
            if all(c in '0123456789abcdef' for c in hex_data):
                encoded_data = EnC_AEs(hex_data)
                self.PaYload = bytes.fromhex(encoded_data)
            else:
                print("❌ بيانات غير صالحة للتشفير")
                self.PaYload = self.dT
        except Exception as encoding_error:
            print(f"❌ خطأ في التشفير: {encoding_error}")
            self.PaYload = self.dT
        
        try:
            self.ResPonse = requests.post(self.UrL, headers=self.HeadErs, data=self.PaYload, verify=False, timeout=30)
            
            if self.ResPonse.status_code == 200 and len(self.ResPonse.text) > 10:
                try:
                    if self.ResPonse.content:
                        hex_content = self.ResPonse.content.hex()
                        self.BesTo_data = json.loads(DeCode_PackEt(hex_content))
                        self.JwT_ToKen = self.BesTo_data['8']['data']           
                        self.combined_timestamp , self.key , self.iv = self.GeT_Key_Iv(self.ResPonse.content)
                        ip , port , ip2 , port2 = self.GeT_LoGin_PorTs(self.JwT_ToKen , self.PaYload)            
                        return self.JwT_ToKen , self.key , self.iv, self.combined_timestamp , ip , port , ip2 , port2
                    else:
                        print("❌ لا توجد بيانات في استجابة التوكن")
                        raise Exception("No data in token response")
                except Exception as e:
                    print(f"❌ خطأ في تحليل استجابة التوكن: {e}")
                    time.sleep(2)
                    return self.ToKen_GeneRaTe(Access_ToKen, Access_Uid)
            else:
                print(f"❌ خطأ في استجابة التوكن، الحالة: {self.ResPonse.status_code}")
                time.sleep(2)
                return self.ToKen_GeneRaTe(Access_ToKen, Access_Uid)
                
        except requests.RequestException as e:
            print(f"❌ خطأ في طلب التوكن: {e}")
            time.sleep(5)
            return self.ToKen_GeneRaTe(Access_ToKen, Access_Uid)
        except Exception as e:
            print(f"❌ خطأ غير متوقع في طلب التوكن: {e}")
            time.sleep(2)
            return self.ToKen_GeneRaTe(Access_ToKen, Access_Uid)
      
    def Get_FiNal_ToKen_0115(self):
        try:
            result = self.Guest_GeneRaTe(self.id , self.password)
            if not result:
                print("❌ فشل في الحصول على التوكنات، إعادة المحاولة...")
                time.sleep(2)
                return self.Get_FiNal_ToKen_0115()
                
            token , key , iv , Timestamp , ip , port , ip2 , port2 = result
            
            if not all([ip, port, ip2, port2]):
                print("❌ فشل في الحصول على البورتات، إعادة المحاولة...")
                time.sleep(2)
                return self.Get_FiNal_ToKen_0115()
                
            self.JwT_ToKen = token        
            try:
                self.AfTer_DeC_JwT = jwt.decode(token, options={"verify_signature": False})
                self.AccounT_Uid = self.AfTer_DeC_JwT.get('account_id')
                self.EncoDed_AccounT = hex(self.AccounT_Uid)[2:]
                self.HeX_VaLue = DecodE_HeX(Timestamp)
                self.TimE_HEx = self.HeX_VaLue
                self.JwT_ToKen_ = token.encode().hex()
            except Exception as e:
                print(f"❌ خطأ في فك التوكن: {e}")
                time.sleep(2)
                return self.Get_FiNal_ToKen_0115()
                
            try:
                self.Header = hex(len(EnC_PacKeT(self.JwT_ToKen_, key, iv)) // 2)[2:]
                length = len(self.EncoDed_AccounT)
                self.__ = '00000000'
                if length == 9: self.__ = '0000000'
                elif length == 8: self.__ = '00000000'
                elif length == 10: self.__ = '000000'
                elif length == 7: self.__ = '000000000'
                else:
                    print('Unexpected length encountered')                
                self.Header = f'0115{self.__}{self.EncoDed_AccounT}{self.TimE_HEx}00000{self.Header}'
                self.FiNal_ToKen_0115 = self.Header + EnC_PacKeT(self.JwT_ToKen_ , key , iv)
            except Exception as e:
                print(f"❌ خطأ في التوكن النهائي: {e}")
                time.sleep(5)
                return self.Get_FiNal_ToKen_0115()
                
            self.AutH_ToKen = self.FiNal_ToKen_0115
            self.Connect_SerVer(self.JwT_ToKen , self.AutH_ToKen , ip , port , key , iv , ip2 , port2)        
            return self.AutH_ToKen , key , iv
            
        except Exception as e:
            print(f"❌ خطأ في Get_FiNal_ToKen_0115: {e}")
            time.sleep(10)
            return self.Get_FiNal_ToKen_0115()

ACCOUNTS = []

def load_accounts_from_file(filename="accs.txt"):
    accounts = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    if ":" in line:
                        parts = line.split(":")
                        if len(parts) >= 2:
                            account_id = parts[0].strip()
                            password = parts[1].strip()
                            accounts.append({'id': account_id, 'password': password})
                    else:
                        accounts.append({'id': line.strip(), 'password': ''})
        print(f"✅ تم تحميل {len(accounts)} حساب من {filename}")
    except FileNotFoundError:
        print(f"❌ ملف {filename} غير موجود!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء قراءة الملف: {e}")
    
    return accounts

ACCOUNTS = load_accounts_from_file()

if not ACCOUNTS:
    ACCOUNTS = [{'id': '4173444648', 'password': '6F0D6506AE64A0B02657DE5CFAFF3988E3D2A3EE28C2B83AF54591D925606140'}]

def start_account(account):
    try:
        FF_CLient(account['id'], account['password'])
    except Exception as e:
        print(f"❌ Error starting account {account['id']}: {e}")
        time.sleep(2)
        start_account(account)

def background_tasks():
    while True:
        try:
            time.sleep(60 * 30)
        except Exception as e:
            time.sleep(60)

@app.route('/api/ghost_attack', methods=['GET'])
def api_ghost_attack():
    try:
        teamcode = request.args.get('teamcode')
        name = request.args.get('name', 'MERO')
        
        if not teamcode:
            return jsonify({
                "success": False,
                "message": "Teamcode is required"
            }), 400
        
        if not ChEck_Commande(teamcode):
            return jsonify({
                "success": False,
                "message": "Invalid teamcode format"
            }), 400
        
        clients_list = get_random_accounts(3)
        
        if not clients_list:
            return jsonify({
                "success": False,
                "message": "No connected accounts available"
            }), 503
            
        success_count = 0
        threads = []
        results = []
        
        for i, client in enumerate(clients_list, 1):
            thread = threading.Thread(target=lambda c=client, r=results: r.append(
                execute_blrx_command(c, teamcode, name, "api_user", i)))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=60)
        
        success_count = sum(results)
        
        return jsonify({
            "success": True,
            "message": f"Ghost attack completed successfully",
            "teamcode": teamcode,
            "name": name,
            "accounts_used": len(clients_list),
            "successful_attacks": success_count,
            "release_version": current_release_version,
            "server_domain": current_server_domain,
            "play_version": current_play_version
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@app.route('/api/ghost', methods=['GET'])
def api_ghost():
    try:
        teamcode = request.args.get('teamcode')
        name = request.args.get('name', 'MERO')
        
        if not teamcode:
            return jsonify({
                "success": False,
                "message": "Teamcode is required"
            }), 400
        
        if not ChEck_Commande(teamcode):
            return jsonify({
                "success": False,
                "message": "Invalid teamcode format"
            }), 400
        
        clients_list = get_random_accounts(3)
        
        if not clients_list:
            return jsonify({
                "success": False,
                "message": "No connected accounts available"
            }), 503
            
        success_count = 0
        threads = []
        results = []
        
        for i, client in enumerate(clients_list, 1):
            thread = threading.Thread(target=lambda c=client, r=results: r.append(
                execute_ghost_command(c, teamcode, name, "api_user", i, clients_list)))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=60)
        
        success_count = sum(results)
        
        return jsonify({
            "success": True,
            "message": f"Ghost successfully",
            "teamcode": teamcode,
            "name": name,
            "accounts_used": len(clients_list),
            "successful_attacks": success_count,
            "release_version": current_release_version,
            "server_domain": current_server_domain,
            "play_version": current_play_version
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    try:
        with connected_clients_lock:
            accounts_count = len(connected_clients)
            accounts_list = list(connected_clients.keys())
        
        return jsonify({
            "status": "online",
            "connected_accounts": accounts_count,
            "active_accounts": accounts_list[:10],
            "total_accounts_loaded": len(ACCOUNTS),
            "release_version": current_release_version,
            "server_domain": current_server_domain,
            "play_version": current_play_version
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def start_accounts():
    print("⏳ جاري بدء تشغيل الحسابات...")

    if not ACCOUNTS:
        print("❌ لا توجد حسابات لبدء التشغيل!")
        return
    
    accounts_to_start = ACCOUNTS[:99999999999]
    print(f"🔧 سيتم تشغيل {len(accounts_to_start)} حساب من أصل {len(ACCOUNTS)}")
    
    for i, account in enumerate(accounts_to_start, 1):
        try:
            print(f"🚀 بدء الحساب {i}: {account['id']}")
            threading.Thread(target=start_account, args=(account,), daemon=True).start()
            time.sleep(0.1)
        except Exception as e:
            print(f"❌ خطأ في بدء الحساب {account['id']}: {e}")

def StarT_SerVer():
    fetch_latest_data()
    start_accounts()

    threading.Thread(target=background_tasks, daemon=True).start()
   # threading.Thread(target=AuTo_ResTartinG, daemon=True).start()
    
    print(f"✅ تم بدء تشغيل النظام بالكامل بنجاح")
    print(f"🕒 وقت البدء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 عدد الحسابات المحملة: {len(ACCOUNTS)}")
    print(f"🔧 عدد الحسابات المشغلة: {min(5, len(ACCOUNTS))}")
    print(f"🌐 API Server running on http://127.0.0.1:5000")
    
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    StarT_SerVer()