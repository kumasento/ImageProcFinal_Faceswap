
import sys
import os
import cv2
from facerepl import *

from facelib.facepp import API, File
from facelib.faceinfo import FaceInfo, FacePose, FaceLandmark
from facelib.facerank import FaceRank
from facelib.faceposebin import FacePoseBin

DEFAULT_POSEBIN_PATH = 'posebin'
DEFAULT_NUM_TOP = 6
DEFAULT_OUT_PREFIX = 'tmp_'

API_KEY = 'bf7eae5ed9cf280218450523049d5f94'
API_SECRET = 'o6SeKJTnaoczTb-j6PBEGXvkiVz2hp71'
api = API(API_KEY, API_SECRET)

def faceswap(img_name):
	img_parsed_name = (img_name.split('/')[-1]).split('.')[-2]
	print img_parsed_name
	img = cv2.imread(img_name)
	posebin = FacePoseBin(DEFAULT_POSEBIN_PATH)

	rst = api.detection.detect(img = File(img_name), attribute='pose')
	img_width = rst['img_width']
	img_height = rst['img_height']
	face = rst['face'][0]
	face_id = face['face_id']
	landmark = api.detection.landmark(face_id = face_id, type='25p')
	pose = face['attribute']['pose']
	face_pose = FacePose(pose)
	face_landmark = FaceLandmark(landmark['result'][0]['landmark'], img_width, img_height)

	cur_face_info = FaceInfo()
	cur_face_info.pose = face_pose
	cur_face_info.landmark = face_landmark

	face_posebin_id = posebin.get_pose_bin_id(face_pose.yaw, face_pose.pitch)
	print face_id
	print face_pose
	print face_landmark
	print 'current face has posebin id %d' % face_posebin_id
	cur_face_info.pose_bin_id = face_posebin_id

	rank = FaceRank(cur_face_info, posebin)
	faceinfos = rank.rank()

	print "found and sorted %d faces" % len(faceinfos)

	ret_names = []
	for faceinfo in faceinfos[0:DEFAULT_NUM_TOP]:
		src_name = "%s/%d/%s.png" % (posebin.path, faceinfo.pose_bin_id, faceinfo.name)
		dst_name = img_name
		print src_name
		swap_img = facecloning.faceclone(src_name, dst_name)
		swap_name = DEFAULT_OUT_PREFIX+img_parsed_name+'_'+faceinfo.name+'.png'
		cv2.imwrite(swap_name, swap_img)

		ret_names.append(swap_name)
	return ret_names


if __name__ == '__main__':
	if len(sys.argv) <= 1:
		print "usage: %s <image>" % sys.argv[0]
		exit(1)

	print "swapping face %s ..." % sys.argv[1]
	print faceswap(sys.argv[1])
