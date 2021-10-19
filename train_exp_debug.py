import sys
import os
#import shutil

def _add_sys_path(new_sys_path):
    if new_sys_path not in sys.path:
        if os.path.isdir(new_sys_path):
            print("add sys.path", new_sys_path)
            sys.path.append(new_sys_path)

def extend_sys_paths():
    this_folder = os.path.dirname(__file__)
    parent_folder = os.path.dirname(this_folder)

    new_sys_path = parent_folder + "/pim"
    _add_sys_path(new_sys_path)

    new_sys_path = parent_folder 
    _add_sys_path(new_sys_path)


extend_sys_paths()

def _change_path(org_path):
    if os.name != "nt":
        return org_path
    new_path = org_path.replace("/", "\\")
    return new_path

def prepare_cmd(root_app, pm_local_trainval):
    hp_network = "mobilenetv3_small_075"
    # hp_saved_checkpoint_version = "checkpoint_10011702:v6"
    # hp_saved_uri_model_best_pim = 'ethanone/pim_{}/{}'.format(hp_network, hp_saved_checkpoint_version)
    # hp_saved_uri_model_best_pim = None

    hp_x_model_tar = "{}/x_model/model_best.pth.tar".format(root_app)
    hp_x_model_tar = _change_path(hp_x_model_tar)

    hp_dataset = "../" + pm_local_trainval
    hp_dataset = _change_path(hp_dataset)

    hp_warmup_epochs_scratch = 6
    hp_epochs_scratch = 200
    hp_cooldown_epochs_scratch = 10

    hp_warmup_epochs_fineturn = 3
    hp_epochs_fineturn = 100
    hp_cooldown_epochs_fineturn = 5

    hp_patience_epochs = 10
    hp_enable_ema = True

    hp_batch_size = 256
    #hp_num_classes = len(odn.keys())
    hp_num_classes = 60

    #hp_class_map = False

    #hp_skip_flags = "sk_training:sk_validate:"
    #hp_skip_flags = "sk_validate:"
    cmd = ""
    cmd += "./train_exp.py "

    cmd += "{} ".format(hp_dataset)

    cmd += "--model {} ".format(hp_network)
    cmd += "--batch-size {} ".format(hp_batch_size)
    cmd += "--experiment pim_{} ".format(hp_network)
    cmd += "--num-classes {} ".format(hp_num_classes)

    cmd += "--sched cosine "
    cmd += "--reprob 0.5 "
    cmd += "--remode pixel "

    #cmd += "--jsd "
    cmd += "--amp "
    cmd += "-j 4 "

    if hp_enable_ema:
        cmd += "--model-ema --model-ema-decay 0.99 "

    cmd += "--log-wandb "
    cmd += "--patience-epochs {} ".format(hp_patience_epochs)

    if os.path.isfile(hp_x_model_tar):
        cmd += "--initial-checkpoint {} ".format(hp_x_model_tar)
        cmd += "--warmup-epochs {} ".format(hp_warmup_epochs_fineturn)
        cmd += "--epochs {} ".format(hp_epochs_fineturn)
        cmd += "--cooldown-epochs {} ".format(hp_cooldown_epochs_fineturn)
        cmd += "--lr 0.1 "
        cmd += "--scale 0.6 1.6 "
        cmd += "--ratio 0.6 1.6 "
        #cmd += "--aug-splits 2 "
    else:
        cmd += "--warmup-epochs {} ".format(hp_warmup_epochs_scratch)
        cmd += "--epochs {} ".format(hp_epochs_scratch)
        cmd += "--cooldown-epochs {} ".format(hp_cooldown_epochs_scratch)
        cmd += "--lr 0.2 "
        cmd += "--scale 0.8 1.2 "
        cmd += "--ratio 0.8 1.2 "
        #cmd += "--aug-splits 2 "

    #cmd += "--aa rand-m9-mstd0.5-inc1 "

    # augmentation
    cmd += "--hflip 0.0 "
    cmd += "--vflip 0.0 "
    cmd += "--color-jitter 0.4 "

    cmd = cmd.strip()
    print(cmd)
    return cmd

def alter_env(root_app, pm_local_trainval):
    os.chdir(root_app)
    cmd = prepare_cmd(root_app, pm_local_trainval)
    
    sys.argv = cmd.split(" ")
    return cmd


def do_tain_exp(root_app, pm_local_trainval):
    from pim.train_exp import main
    alter_env(root_app, pm_local_trainval)
    main()


if __name__ == "__main__":
    folder_this = os.path.dirname(__file__)

    root_app = folder_this
    pm_local_trainval = "dx_pim_images"
    do_tain_exp(root_app, pm_local_trainval)

