import os, json, requests, runpod

import torch
from PIL import Image
import numpy as np
from nodes import NODE_CLASS_MAPPINGS
from nodes import load_custom_node

def download_file(url, save_dir, file_name):
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, file_name)
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path

load_custom_node("/content/ComfyUI/custom_nodes/ComfyUI-AdvancedLivePortrait")
LoadImage = NODE_CLASS_MAPPINGS["LoadImage"]()
ExpressionEditor = NODE_CLASS_MAPPINGS["ExpressionEditor"]()

@torch.inference_mode()
def generate(input):
    values = input["input"]

    src_image=values['input_image_check']
    src_image=download_file(url=src_image, save_dir='/content', file_name='src_image')
    rotate_pitch=values['rotate_pitch']
    rotate_yaw=values['rotate_yaw']
    rotate_roll=values['rotate_roll']
    blink=values['blink']
    eyebrow=values['eyebrow']
    wink=values['wink']
    pupil_x=values['pupil_x']
    pupil_y=values['pupil_y']
    aaa=values['aaa']
    eee=values['eee']
    woo=values['woo']
    smile=values['smile']
    src_ratio=values['src_ratio']
    sample_ratio=values['sample_ratio']
    sample_parts=values['sample_parts']
    crop_factor=values['crop_factor']
    
    src_image = LoadImage.load_image(src_image)[0]
    output_image = ExpressionEditor.run(rotate_pitch, rotate_yaw, rotate_roll, blink, eyebrow, wink, pupil_x, pupil_y, aaa, eee, woo, smile, src_ratio, 
                                        sample_ratio, sample_parts, crop_factor, src_image=src_image, sample_image=None, motion_link=None, add_exp=None)
    Image.fromarray(np.array(output_image['result'][0]*255, dtype=np.uint8)[0]).save('/content/advanced-live-portrait-tost.png')

    result = "/content/advanced-live-portrait-tost.png"
    try:
        notify_uri = values['notify_uri']
        del values['notify_uri']
        notify_token = values['notify_token']
        del values['notify_token']
        discord_id = values['discord_id']
        del values['discord_id']
        if(discord_id == "discord_id"):
            discord_id = os.getenv('com_camenduru_discord_id')
        discord_channel = values['discord_channel']
        del values['discord_channel']
        if(discord_channel == "discord_channel"):
            discord_channel = os.getenv('com_camenduru_discord_channel')
        discord_token = values['discord_token']
        del values['discord_token']
        if(discord_token == "discord_token"):
            discord_token = os.getenv('com_camenduru_discord_token')
        job_id = values['job_id']
        del values['job_id']
        default_filename = os.path.basename(result)
        with open(result, "rb") as file:
            files = {default_filename: file.read()}
        payload = {"content": f"{json.dumps(values)} <@{discord_id}>"}
        response = requests.post(
            f"https://discord.com/api/v9/channels/{discord_channel}/messages",
            data=payload,
            headers={"Authorization": f"Bot {discord_token}"},
            files=files
        )
        response.raise_for_status()
        result_url = response.json()['attachments'][0]['url']
        notify_payload = {"jobId": job_id, "result": result_url, "status": "DONE"}
        web_notify_uri = os.getenv('com_camenduru_web_notify_uri')
        web_notify_token = os.getenv('com_camenduru_web_notify_token')
        if(notify_uri == "notify_uri"):
            requests.post(web_notify_uri, data=json.dumps(notify_payload), headers={'Content-Type': 'application/json', "Authorization": web_notify_token})
        else:
            requests.post(web_notify_uri, data=json.dumps(notify_payload), headers={'Content-Type': 'application/json', "Authorization": web_notify_token})
            requests.post(notify_uri, data=json.dumps(notify_payload), headers={'Content-Type': 'application/json', "Authorization": notify_token})
        return {"jobId": job_id, "result": result_url, "status": "DONE"}
    except Exception as e:
        error_payload = {"jobId": job_id, "status": "FAILED"}
        try:
            if(notify_uri == "notify_uri"):
                requests.post(web_notify_uri, data=json.dumps(error_payload), headers={'Content-Type': 'application/json', "Authorization": web_notify_token})
            else:
                requests.post(web_notify_uri, data=json.dumps(error_payload), headers={'Content-Type': 'application/json', "Authorization": web_notify_token})
                requests.post(notify_uri, data=json.dumps(error_payload), headers={'Content-Type': 'application/json', "Authorization": notify_token})
        except:
            pass
        return {"jobId": job_id, "result": f"FAILED: {str(e)}", "status": "FAILED"}
    finally:
        if os.path.exists(result):
            os.remove(result)

runpod.serverless.start({"handler": generate})