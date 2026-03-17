import functools
from .rig import *
from .surface import update_fit_surface_curve_data


def _normalize_sample(sample):
    if isinstance(sample, int):
        return ["param", "length", "topo"][min(max(sample, 0), 2)]
    if isinstance(sample, str):
        return sample
    return "param"


class Loop(RigSystem):
    fit_configs = dict(Loop=dict(pre="", fit="loop_surface", names=["Orbita", "LipOut"], rml="RML"))
    fit_kwargs = [(dict(), dict(cluster=3, joint=12, degree=2, sample="param"))]

    def rig_rml(self, fits):
        surface = fits.find(suf="Surface")
        up_node = fits.find(suf="Up")
        dn_node = fits.find(suf="Dn")
        
        if not surface or not up_node or not dn_node:
            missing = []
            if not surface: missing.append("Surface")
            if not up_node: missing.append("Up")
            if not dn_node: missing.append("Dn")
            
            # Extract short names by splitting on '|' and taking the last element
            conflict_nodes = [node["node"].split('|')[-1] for node in fits.data if "node" in node]
            node_list_str = ", ".join(conflict_nodes)
            
            error_msg = u"[%s] 绑定生成中断！\n原因: 该部位缺少关键节点属性或归类(classify)冲突。\n缺失: %s\n需要修正的节点: %s\n解决: 请在大纲中将上述错误节点的分类改回原部位或将其删除！" % (
                self.root.name, 
                ", ".join(missing),
                node_list_str
            )
            import maya.cmds as cmds
            cmds.error(error_msg)
            raise RuntimeError(error_msg)
            
        up = self.rig_loop_ud("Up", up_node["node"], **surface)
        dn = self.rig_loop_ud("Dn", dn_node["node"], **surface)
        for k, v in dn.items():
            up[k] = list(up[k]) + list(reversed(v))[1:-1]
        wts = get_cluster_weights(len(up["clusters"]), up["us"], degree=surface["degree"], close=True)
        set_jac_weights(up["clusters"], up["joints"], wts)

    @staticmethod
    def rig_loop_ud(ud, curve, joint, cluster, sample="param", mirror=False, **kwargs):
        fit_kwargs = dict(kwargs)
        fit_kwargs["mirror"] = mirror
        sample = _normalize_sample(sample)
        matrices = functools.partial(get_fit_surface_curve_matrices, **fit_kwargs)
        if joint < 0:
            points = get_fit_cv_points(node=curve, mirror=mirror)
            joint_us = get_us_by_points(points, False)
            joint_ud_us = update_us(ud, joint_us)
            joint_matrices = get_fit_curve_matrices(points, joint_ud_us, **fit_kwargs)
        else:
            if sample in ("length", "topo"):
                if sample == "length":
                    points = get_points_by_curve(curve, joint)
                    if mirror:
                        points = mirror_points(points)
                else:
                    points = get_fit_cv_points(node=curve, mirror=mirror)
                    points = resample_polyline_points(points, joint, False)
                joint_us = get_us_by_points(points, False)
                joint_ud_us = update_us(ud, joint_us)
                joint_matrices = get_fit_curve_matrices(points, joint_ud_us, **fit_kwargs)
            else:
                joint_us = get_curve_parameter_list(joint, False)
                joint_ud_us = update_us(ud, joint_us)
                joint_matrices = matrices(joint_ud_us)
        fmt = Fmt(merge_ud=True, ud=ud, cluster=cluster, joint=len(joint_matrices), **kwargs)
        joints, ctrls = add_joint_ctrls(fmt.joins(), joint_matrices)
        cluster_us = update_us(ud, get_curve_parameter_list(cluster, False))
        clusters, ctrls = add_cluster_ctrls(fmt.clusters(), matrices(cluster_us))
        ctrls_follow_joints(ctrls, joints, close=False, us=joint_us)
        return dict(clusters=clusters, joints=joints, us=joint_ud_us)


def update_us(ud, us):
    if ud == "Up":
        return [u*0.5 for u in us]
    else:
        return [1.0-u*0.5 for u in us]

