# ACDC

ACDC, or the Adverse Conditions Dataset with Correspondences, is a large-scale dataset for dense semantic perception tasks in adverse visual conditions, including semantic segmentation, object detection, and panoptic segmentation. It consists of 4006 images which are evenly distributed between four common adverse conditions: fog, nighttime, rain, and snow. Each adverse-condition image comes with a high-quality fine pixel-level panoptic annotation, a corresponding image of the same scene taken under normal conditions, and a binary mask that distinguishes between intra-image regions of clear and uncertain semantic content. Moreover, ACDC includes high-quality fine pixel-level panoptic annotations for 1503 of the aforementioned corresponding normal-condition images.

Thus, ACDC supports:
1. semantic segmentation
2. object detection
3. panoptic segmentation
4. the new uncertainty-aware semantic segmentation

The ground-truth annotations of the training and validation sets are publicly available. The ground-truth annotations of the test set are withheld and they are used for the publicly available [ACDC benchmark][acdc_benchmark].


### Download

ACDC can be downloaded through the associated [website][acdc_website]. Users need to register on this website first before accessing the dataset.

**Note**: due to data protection regulations, the original RGB images of the dataset, which contain personal data, are not made available by default. After having registered, users who are interested in the original images need to explicitly request access to them. Anonymized versions of the images - with minimal modifications - are available by default and can be used alternatively.


### Dataset Structure

The directory structure of ACDC is as follows:
```
{root}/{type}/{condition}/{split}/{sequence}/{sequence}_frame_{frame:0>6}_{type}{ext}`
```

The meaning of the individual directory levels is:
 - `root`      the root directory where the dataset is stored.
 - `type`      the type/modality of data, e.g. `rgb_anon` for anonymized RGB images, or `gt` for ground-truth annotations.
 - `condition` the adverse condition associated with the data, e.g. `night`.
 - `split`     the split, e.g. `train`. Note that not all types of data exist for all splits.
 - `sequence`  the image sequence, e.g. `GOPR0351`.

Possible values of `type`:
 - `rgb`      the original RGB `png` images in 8-bit format.
 - `rgb_anon` the anonymized RGB `png` images in 8-bit format.
 - `gt`       the pixel-level semantic annotations and invalid mask annotations. Annotations are encoded using `png` images, where pixel values encode labels. There are three different formats for the semantic annotations and two formats for the invalid mask annotations. Details on these formats are given below.

For benchmarking on annotated normal-condition images, a `test_ref_image_list.txt` file which includes the paths to the set of annotated images in the `test_ref` split is provided under `gt`.

Possible values of `condition`:
 - `fog`
 - `night`
 - `rain`
 - `snow`

Possible values of `split`:
 - `train`     training set. It contains 400 images from each of the four examined adverse conditions.
 - `train_ref` corresponding normal-condition images for the training set.
 - `val`       validation set. It contains 100 images from each of fog, rain, and snow, and 106 images from night.
 - `val_ref`   corresponding normal-condition images for the validation set.
 - `test`      test set. It contains 500 images from each of the four examined adverse conditions.
 - `test_ref`  corresponding normal-condition images for the test set.

The meaning of the individual constituents of the file name format is:
 - `ext`                an optional identifier `_ref` for files in the splits `train_ref`, `val_ref` and `test_ref`, followed by an optional suffix `_{suffix}` (only relevant for `gt` files), in turn followed by the extension of the file , e.g. `_ref_labelIds.png` for semantic annotations of corresponding normal-condition images.
 - `frame:0>6`          the frame number within the respective sequence, composed of six digits.

Possible values of `suffix` (for `gt` files):
 - `labelIds`      semantic labels encoded using `png` images, where pixel values encode labels in Cityscapes IDs format. Please refer to the script [helpers/labels.py][cityscapes_labels_docs] in the [Cityscapes GitHub repository][cityscapesGithub] for details on the 19 semantic classes included in our semantic annotations, which coincide with the classes that are included in Cityscapes evaluation.
 - `labelTrainIds` semantic labels encoded using `png` images, where pixel values encode labels in Cityscapes trainIDs format.
 - `labelColor`    semantic labels encoded using `png` images, where pixel values encode labels in Cityscapes color format. Purposed for visualization.
 - `invIds`        invalid masks encoded using 8-bit `png` images, where the value of invalid pixels is set to `1` and the value of valid pixels is set to `0`. This suffix is only relevant for files that are not in the `*_ref` splits.
 - `invGray`       invalid masks encoded using 8-bit `png` images, where the value of invalid pixels is set to `255` and the value of valid pixels is set to `0`. Purposed for visualization.  This suffix is only relevant for files that are not in the `*_ref` splits.


### Dataset Structure for detection and panoptic segmentation annotations

The provided detection annotations follow the [COCO format][coco_format]. 

The directory structure of ACDC detection annotations is as follows:

```
├── fog
│   ├── instancesonly_fog_test_image_info.json
│   ├── instancesonly_fog_train_gt_detection.json
│   └── instancesonly_fog_val_gt_detection.json
├── night
│   ├── instancesonly_night_test_image_info.json
│   ├── instancesonly_night_train_gt_detection.json
│   └── instancesonly_night_val_gt_detection.json
├── rain
│   ├── instancesonly_rain_test_image_info.json
│   ├── instancesonly_rain_train_gt_detection.json
│   └── instancesonly_rain_val_gt_detection.json
└── snow
│   ├── instancesonly_snow_test_image_info.json
│   ├── instancesonly_snow_train_gt_detection.json
│   └── instancesonly_snow_val_gt_detection.json
├── instancesonly_test_image_info.json
├── instancesonly_test_ref_image_info.json
├── instancesonly_train_gt_detection.json
├── instancesonly_train_gt_ref_detection.json
├── instancesonly_val_gt_detection.json
└── instancesonly_val_gt_ref_detection.json
```

Detection annotation json files for different conditions are placed in the path 
```
{root}/gt_detection/{condition}/instancesonly_{condition}_{split}_{type}.json
```

Here `condition` is optional. It could be `fog`, `night`, `rain`, `snow` or it can be empty. 

`type` could be `gt_detection`, `gt_ref_detection` or `image_info`. `gt_detection` refers to ground-truth annotations, which is applied to the `train` and `val` splits. `gt_ref_detection` refers to ground-truth annotations for corresponding normal-condition images, which is applied to the `train_ref` and `val_ref` splits. `image_info` only contains the list of images and the predefined categories, which is applied to the `test` and `test_ref` splits. 

The provided panoptic segmentation annotations also follow the [COCO format][coco_format]. 

The directory structure of ACDC panoptic segmentation annotations is as follows:
```
├── fog
│   ├── fog_test_image_info.json
│   ├── fog_train_gt_panoptic.json
│   ├── fog_val_gt_panoptic.json
│   ├── test
│   ├── train
│   ├── val
│   ├── test_ref
│   ├── train_ref
│   └── val_ref
├── night
│   ├── night_test_image_info.json
│   ├── night_train_gt_panoptic.json
│   ├── night_val_gt_panoptic.json
│   ├── test
│   ├── train
│   ├── val
│   ├── test_ref
│   ├── train_ref
│   └── val_ref
├── rain
│   ├── rain_test_image_info.json
│   ├── rain_train_gt_panoptic.json
│   ├── rain_val_gt_panoptic.json
│   ├── test
│   ├── train
│   ├── val
│   ├── test_ref
│   ├── train_ref
│   └── val_ref
├── snow
│   ├── snow_test_image_info.json
│   ├── snow_train_gt_panoptic.json
│   ├── snow_val_gt_panoptic.json
│   ├── test
│   ├── train
│   ├── val
│   ├── test_ref
│   ├── train_ref
│   └── val_ref
├── test_image_info.json
├── test_ref_image_info.json
├── train_gt_panoptic.json
├── train_gt_ref_panoptic.json
├── val_gt_panoptic.json
└── val_gt_ref_panoptic.json
```

For panoptic segmentation, the semantic annotation json files for different conditions are placed in the path 
```
{root}/gt_panoptic/{condition}/{condition}_{split}_{type}.json`
```

Here `condition` is optional. It could be `fog`, `night`, `rain`, `snow` or it can be empty.

`type` could be `gt_panoptic`, `gt_ref_panoptic` or `image_info`. `gt_panoptic` refers to ground-truth annotations, which is applied to the `train` and `val` splits. `gt_ref_panoptic` refers to ground-truth annotations for corresponding normal-condition images, which is applied to the `train_ref` and `val_ref` splits. `image_info` only contains the list of images and the predefined categories, which is applied to the `test` and `test_ref` splits. 

The pixel-level panoptic mask PNG files are placed in the path 
```
{root}/gt_panoptic/{condition}/{split}/{sequence}/{sequence}_frame_{frame:0>6}_{type}.png`
```

### Citation

If you use ACDC in your work, please cite our publications as listed on the [ACDC website][acdc_citation].


### License

ACDC is made available for non-commercial use under the license agreement which is contained in the attached file `License.pdf`.


### Contact

Please feel free to contact us with any questions or comments:

Christos Sakaridis, Haoran Wang, Dengxin Dai
acdc.dataset [at] zohomail.eu
https://acdc.vision.ee.ethz.ch

[acdc_website]: <https://acdc.vision.ee.ethz.ch>
[acdc_benchmark]: <https://acdc.vision.ee.ethz.ch/benchmarks>
[acdc_citation]: <https://acdc.vision.ee.ethz.ch/citation>
[cityscapesGithub]: <https://github.com/mcordts/cityscapesScripts>
[cityscapes_labels_docs]: <https://github.com/mcordts/cityscapesScripts/blob/master/cityscapesscripts/helpers/labels.py>
[coco_format]: <https://cocodataset.org/#format-data>
