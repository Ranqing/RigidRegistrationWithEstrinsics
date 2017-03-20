import numpy as np
import os
import plyfile


def listdir(
        fd, isfile=False, isdir=False,
        startswith=None, endswith=None, contains=None,
        ignore_prefix=None, ignore_suffix=None, ignore_anywhere=None,
        fullpath=False, sort=True):
    ''' os.listdir
        isfile, list files only
        isdir, list dirs only
        startswith, case insensitive
        endswith, case insensitive
        contains, case insensitive
        ignore_prefix, case insensitive
        ignore_suffix, case insensitive
        ignore_anywhere, case insensitive
        fullpath, os.path.join(fd, i) for i in rs
        sort, default is True
    '''
    rs = [i for i in os.listdir(fd) if not i.endswith('.DS_Store')]
    if isfile:
        rs = [i for i in rs if os.path.isfile(os.path.join(fd, i))]
    if isdir:
        rs = [i for i in rs if os.path.isdir(os.path.join(fd, i))]
    if startswith is not None:
        rs = [i for i in rs if i.lower().startswith(startswith.lower())]
    if endswith is not None:
        rs = [i for i in rs if i.lower().endswith(endswith.lower())]
    if contains is not None:
        rs = [i for i in rs if contains.lower() in i.lower()]
    if ignore_prefix is not None:
        rs = [i for i in rs if not i.lower().startswith(ignore_prefix.lower())]
    if ignore_suffix is not None:
        rs = [i for i in rs if not i.lower().endswith(ignore_suffix.lower())]
    if ignore_anywhere is not None:
        rs = [i for i in rs if ignore_anywhere.lower() not in i.lower()]
    if fullpath:
        rs = [os.path.join(fd, i) for i in rs]
    if sort:
        rs.sort()
    return rs


def read_string_lines(file, ignore_comment=True):
    ''' ignore comment line starts with '#', default True
        remove '\n' at the end of line
    '''
    with open(file, 'r') as f:
        rs = [i.strip() for i in f.readlines()
              if not ignore_comment or not i.startswith('#')]
    return rs


def str_2_float(s):
    try:
        rs = float(s)
    except:
        rs = s
    return rs


def read_multiple_float_lines(file):
    ''' ignore comment
        if float(element) fails, keep it as a string
        return [[1.0, 2.0], ...]
    '''
    lines = read_string_lines(file)
    rs = [[str_2_float(k) for k in i.split()] for i in lines]
    return rs


def extract_extrinsic_filename(fn):
    rs = fn[len('FRM_0259_pointcloud_'):]
    rs = rs[0] + '-' + rs[1:3] + '.txt'
    return rs


def read_extrinsic(fn):
    data = read_multiple_float_lines(fn)
    R = np.matrix([data[3], data[4], data[5]])
    T = np.matrix(data[6]).transpose()
    return R, T


def trans(vertex, r, t):
    for i in range(vertex.count):
        x = vertex[i][0]
        y = vertex[i][1]
        z = vertex[i][2]
        p_cam_coord = np.matrix([x, y, z]).transpose()
        e = r.transpose() * p_cam_coord + t * 2520.14577222
        vertex[i][0] = e[0, 0]
        vertex[i][1] = e[1, 0]
        vertex[i][2] = e[2, 0]


def process(f_in, f_ex, f_rs):
    r, t = read_extrinsic(f_ex)
    ply = plyfile.PlyData.read(f_in)
    trans(ply['vertex'], r, t)
    ply.write(f_rs)
    print(f_rs, 'finished')


def main():
    root_fd = '.'
    in_name = 'FRM_0245'
    res_name = in_name + '_registered'

    fd_in = os.path.join(root_fd, in_name)
    fd_extrinsic = os.path.join(root_fd, 'extrinsic_res_inc')

    fd_res = os.path.join(root_fd, res_name)
    if not os.path.exists(fd_res):
        os.makedirs(fd_res)

    files = listdir(fd_in, endswith='ply', ignore_prefix='coord')
    for idx, f in enumerate(files):
        f_i = os.path.join(fd_in, f)
        f_e = os.path.join(fd_extrinsic, extract_extrinsic_filename(f))
        f_r = os.path.join(fd_res, f)
        process(f_i, f_e, f_r)
        if idx == 1:
            continue


if __name__ == '__main__':
    main()
