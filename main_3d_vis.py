'''
Descripttion: this file will be used 
version: 
Author: ThreeStones1029 221620010039@qq.com
Date: 2023-07-18 16:58:07
LastEditors: ShuaiLei
LastEditTime: 2025-03-10 20:13:11
'''
import os
import numpy as np
import open3d as o3d
import nibabel as nib
from dataset_tools.dataset_sample import Dataset_sample
from drr_tools.drr_image_postprocess import blackwhite_inverse_images
from visual_tools.view_3d import draw3d, draw_multiview_3d
from drr_tools.genDRR import genDRR, gen_multiDRRs
from io_tools.file_management import load_json_file


# 这个是用来生成单张的图像和展示3D效果的
def generate_and_show3d_single_view():
    sdr = 500
    height = 1000
    delx = 0.5
    ctDir = "data/ct_mask/cao_fei/caofei.nii.gz"
    ct_image = nib.load(ctDir)
    header = ct_image.header
    volume = ct_image.shape
    spacing = header['pixdim'][1:4]
    cuboid_center = [0, 0, sdr]
    Initial_coordinate = list([header["qoffset_x"], header["qoffset_y"],-header["qoffset_z"]])
    # 加载3D模型，并且移动到方框内
    mesh = o3d.io.read_triangle_mesh("data/ct_mask/cao_fei/caofei.ply")
    mesh.translate(Initial_coordinate)
    threshold = 0
    rotations = [90, 180, 180]
    translations = [0, 0, 0]
    saveIMG = "document/single_image_3d_vis.png"
    genDRR(sdr, height, delx, threshold, rotations, translations, ctDir, saveIMG)
    draw3d(volume, spacing, sdr, height, delx, rotations, translations, saveIMG, mesh)


# 这个是用来生成多张的图像和展示3D效果的
def generate_and_show3d_multi_view():
    sdr = 500
    height = 1000
    delx = 0.5
    ctDir = "data/ct_mask/cao_fei/caofei.nii.gz"
    ct_image = nib.load(ctDir)
    header = ct_image.header
    volume = ct_image.shape
    spacing = header['pixdim'][1:4]
    cuboid_center = [0, 0, sdr]
    Initial_coordinate = list([header["qoffset_x"], header["qoffset_y"],-header["qoffset_z"]])

    # 加载3D模型，并且移动到方框内
    mesh = o3d.io.read_triangle_mesh("data/ct_mask/cao_fei/caofei.ply")
    mesh.translate(Initial_coordinate)
    threshold = 0
    AP_rot_range_list = [[90, 90], [180, 180], [150, 210]]
    AP_trans_range_list = [[0, 0], [0, 0], [0, 0]]
    LA_rot_range_list = [[90, 90], [180, 180], [60, 120]]
    LA_trans_range_list = [[0, 0], [0, 0], [0, 0]]
    dataset_sample = Dataset_sample()
    AP_num_samples = 3
    LA_num_samples = 3
    AP_rotations_list, AP_translations_list = dataset_sample.Monte_Carlo_sample_dataset(AP_rot_range_list,AP_trans_range_list, AP_num_samples)
    LA_rotations_list, LA_translations_list = dataset_sample.Monte_Carlo_sample_dataset(LA_rot_range_list,LA_trans_range_list, LA_num_samples)

    rotations_list = AP_rotations_list + LA_rotations_list
    translations_list = AP_translations_list + LA_translations_list
    rotations = np.array(rotations_list, dtype=np.double)
    translations = np.array(translations_list, dtype=np.double)
    save_images_folder = "document"
    ct_name = os.path.basename(ctDir).split(".")[0]
    saveIMG_list = []
    for i in range(AP_num_samples + LA_num_samples):
        saveIMG_list.append(os.path.join(save_images_folder, ct_name + "_" + str(i + 1) + ".png"))
    gen_multiDRRs(sdr, height, delx, threshold, rotations, translations, ctDir, save_images_folder)
    # DRR颜色翻转
    # blackwhite_inverse_images(saveIMG_list)
    draw_multiview_3d(volume, spacing, sdr, height, delx, rotations, translations, saveIMG_list, mesh)


# 这个用于直接可视化已经生成的结果
def show3d_multi_view(vis_segmentation_or_detection):
    dataset = load_json_file("data/verse2020_test_segmentation_dataset/all/gt_bbox.json")
    projection_parameter = dataset["info"]["projection_parameter"]
    sdr = projection_parameter["sdr"]
    height = projection_parameter["height"]
    delx = projection_parameter["delx"]
    ctDir = "data/verse2020_test/verse004/verse004.nii.gz"
    gt_mask_vis_folder = "data/verse2020_test_segmentation_dataset/all/gt_mask_vis"
    gt_bbox_vis_folder = "data/verse2020_test_segmentation_dataset/all/gt_bbox_vis"
    ct_name = os.path.basename(ctDir)
    ct_image = nib.load(ctDir)
    header = ct_image.header
    volume = ct_image.shape
    spacing = header['pixdim'][1:4]
    cuboid_center = [0, 0, sdr]
    Initial_coordinate = list([header["qoffset_x"], header["qoffset_y"],-header["qoffset_z"]])

    # 加载3D模型，并且移动到方框内
    mesh = o3d.io.read_triangle_mesh("data/verse2020_test/verse004/verse004.ply")
    mesh.translate(Initial_coordinate)
    rotations_list = []
    translations_list = []
    saveIMG_list = []
    for image in dataset["images"]:
        if image["ct_name"] == ct_name:
            rotations_list.append(image["rotation"])
            translations_list.append(image["translation"])
            if vis_segmentation_or_detection == "segmentation":
                saveIMG_list.append(os.path.join(gt_mask_vis_folder, image["file_name"]))
            else:
                saveIMG_list.append(os.path.join(gt_bbox_vis_folder, image["file_name"]))

    rotations = np.array(rotations_list, dtype=np.double)
    translations = np.array(translations_list, dtype=np.double)
    draw_multiview_3d(volume, spacing, sdr, height, delx, rotations, translations, saveIMG_list, mesh)


if __name__ == "__main__":
    show3d_multi_view("detection")
