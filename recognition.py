import base64
import httplib
import json
import os
import sys
from playsound import playsound
from PIL import Image, ImageDraw, ImageFont
import csv
import datetime
from firebase import firebase

_print_responses = False
_cloud_token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx"
_cloud_host = "dev.sighthoundapi.com"
_object_ids = set()
_group_name = "family"
_output_folder = "out"
fb = firebase.FirebaseApplication('https://attendance-app-7b374.firebaseio.com/', None)



FindRoll = {
    "Akash":1,
    "Amit":2,
    "Ashutosh":3,
    "Kundan":4,
    "Milton":5,
    "Nischay":6,
    "Sanjeev":7,
    "Shubham":8,
    "Vibhor":9,
    "Zubair":10
}

Names_Of_Students = {
    1:
    {
        "Name":"Akash",
        "Status":"Absent"
    },
    2:
    {
        "Name":"Amit",
        "Status":"Absent"
    },
    3:
    {
        "Name":"Ashutosh",
        "Status":"Absent"
    },
    4:
    {
        "Name":"Kundan",
        "Status":"Absent"
    },
    5:
    {
        "Name":"Milton",
        "Status":"Absent"
    },
    6:
    {
        "Name":"Nischay",
        "Status":"Absent"
    },
    7:
    {
        "Name":"Sanjeev",
        "Status":"Absent"
    },
    8:
    {
        "Name":"Shubham",
        "Status":"Absent"
    },
    9:
    {
        "Name":"Vibhor",
        "Status":"Absent"
    },
    10:
    {
        "Name":"Zubair",
        "Status":"Absent"
    }
}



def send_request(request_method, request_path, params):
    headers = {"Content-type": "application/json",
               "X-Access-Token": _cloud_token}
    conn = httplib.HTTPSConnection(_cloud_host)
    conn.request(request_method, request_path, params, headers)
    response = conn.getresponse()
    body = response.read()
    error = response.status not in [200, 204]

    if _print_responses or error:
        print response.status, body

    if error:
        sys.exit(1)
    return body

def is_image(filename):
    return filename.endswith('.png') or filename.endswith('.jpeg') or \
            filename.endswith('.jpg') or filename.endswith('.bmp')

def step1_upload_images(train_path):
    print "Step 1: Uploading training images"
    for name in os.listdir(train_path):
        base_path = os.path.join(train_path, name)
        if os.path.isdir(base_path):
            print "  Adding images for object id " + name
            for training_file in os.listdir(base_path):
                file_path = os.path.join(base_path, training_file)
                if is_image(file_path):
                    print "    Uploading file " + training_file
                    add_training_image(file_path, name)

                    _object_ids.add(name)

    print "Step 1 complete\n"

def add_training_image(image_path, object_id):
    base64_image = base64.b64encode(open(image_path).read())
    params = json.dumps({"image": base64_image})

    url_path = "/v1/image/%s?train=manual&objectType=person&objectId=%s" % \
            (os.path.basename(image_path), object_id)
    send_request("PUT", url_path, params)

def step2_create_group():
    print "Step 2: Creating group"
    print "  Adding objects %s to group %s" % (str(_object_ids), _group_name)

    params = json.dumps({"objectIds": list(_object_ids)})
    send_request("PUT", "/v1/group/" + _group_name, params)

    print "Step 2 complete\n"


def step3_train_group():
    print "Step 3: Training group"
    print "  Sending train request for group %s" % _group_name

    send_request("POST", "/v1/group/%s/training" % _group_name, None)

    print "Step 3 complete\n"

def step4_test(test_path):
    # RunForever()
    print "Step 4: Beginning tests"
    CaptureImage()
    if not os.path.exists(_output_folder):
        os.mkdir(_output_folder)
    for test_file in os.listdir(test_path):
        file_path = os.path.join(test_path, test_file)
        if not is_image(file_path):
            continue
            return
        print "  Submitting test image " + test_file
        base64_image = base64.b64encode(open(file_path).read())
        params = json.dumps({"image": base64_image})
        url_path = "/v1/recognition?groupId=" + _group_name
        response = json.loads(send_request("POST", url_path, params))

        # Annotate the image
        image = Image.open(file_path)
        font = ImageFont.load_default
        draw = ImageDraw.Draw(image)

        for face in response['objects']:
            # Retrieve and draw a bounding box for the detected face.
            json_vertices = face['faceAnnotation']['bounding']['vertices']
            vert_list = [(point['x'], point['y']) for point in json_vertices]
            draw.polygon(vert_list)

            # Retrieve and draw the id and confidence of the recongition.
            name = face['objectId']

            confidence = face['faceAnnotation']['recognitionConfidence']
            if(confidence>0.5):
                # if(CheckForPresence(name)==0)
                step5_mark_attendance(name,"Present")
                draw.text(vert_list[0], "%s - %s" % (name, confidence))

        image.save(os.path.join(_output_folder, test_file))

    print "Step 4 complete\n"
    # RunForever()

# import cv2
import numpy as np
import cv2
from PIL import Image

def CaptureImage():
    cap = cv2.VideoCapture(0)

    while(True):
        ret, frame = cap.read()
        cv2.imwrite('/home/robhood97/Downloads/sighthound-cloud-tutorial/images/reco-test/test.jpg', frame)
        imageFile = "/home/robhood97/Downloads/sighthound-cloud-tutorial/images/reco-test/test.jpg"
        im1 = Image.open(imageFile)
        width = 560
        height = 400
        im2 = im1.resize((width, height), Image.NEAREST)      # use nearest neighbour
        ext = ".jpg"
        im2.save("/home/robhood97/Downloads/sighthound-cloud-tutorial/images/reco-test/test" + ext)
        break
    cap.release()
    cv2.destroyAllWindows()



def RunForever():
    while(1):
        Check_For_Api()
#
# def CheckForPresence(name):
#     date_root = "/List/"+str(datetime.date.today())
#     result = firebase.get(date_root, None)
#     if(result[FindRoll[name]]["Name"]==name && result[FindRoll[name]]["Status"]=="Present"):
#         return 1
#     else:
#         return 0

    # print(result)

def step5_mark_attendance(name,status):
    # fb = firebase.FirebaseApplication('https://attendance-app-7b374.firebaseio.com/', None)
        # date_now = datetime.datetime.now()
        # fields=[name,"Yes",date_now]
        # f = open(r'attendance.csv', 'a')
        # writer = csv.writer(f)
        # writer.writerow(fields)
        # data = {date_now : [name]}
        # result = firebase.post(date_now, data, {'print': 'pretty'}, {'X_FANCY_HEADER': 'VERY FANCY'})
    date_root = "/List/"+str(datetime.date.today())
    # rssult = CheckForPresence(name)
    # if rssult==0:
    Names_Of_Students[FindRoll[name]]["Status"]=status
    result = fb.patch(date_root, Names_Of_Students)
    playsound("sound.mp3")

def Check_For_Api():
    # firebase = firebase.FirebaseApplication('https://attendance-app-7b374.firebaseio.com/', None)
    result = fb.get('/Data', None)
    if(result==None):
        return
    if(result==1):
        fb.delete("/Data",0)
        # step4_test
        if len(sys.argv) != 2:
            print "Usage: python recognition.py <path to images directory>"
            sys.exit(2)

        root_dir = sys.argv[1]
        step4_test(os.path.join(root_dir, "reco-test"))


if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print "Usage: python recognition.py <path to images directory>"
    #     sys.exit(2)
    #
    # root_dir = sys.argv[1]

    # step1_upload_images(os.path.join(root_dir, "training"))
    # step2_create_group()
    # step3_train_group()
    RunForever()
    # step4_test(os.path.join(root_dir, "reco-test"))
