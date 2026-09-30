"""Prepare one-image-per-pose sprite-gen runs from the accepted native Tique.

Only reference enlargement and numeric requests: no generated animation sheets,
body-part fitting, automatic squashing, or invented character artwork.
"""
from pathlib import Path
from collections import Counter
import hashlib, json
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'art/return-v10-spritegen'
BASE = ROOT / 'unity/TiqueReturnPrototype/Assets/Resources/Return/Tique/Idle/00.png'
POSES = {
    'jump': {
        'preload': 'ONE still pose: gentle anticipation before a jump. Bend both knees slightly, feet planted, both rounded hands sweep a little behind the hips. Keep the solid head and chest intact; the knees create the lower stance.',
        'takeoff': 'ONE still pose: just leaving the floor. Both legs extend under the hips and the two hands sweep forward only to waist height, elbows bent. Full connected arms and legs; this is a restrained small mascot jump.',
        'rise': 'ONE still pose: rising in a small jump. Both feet begin to fold slightly backward at the knees, hands relaxed diagonally down at the sides. Keep the hands clearly visible beyond the chest silhouette.',
        'apex': 'ONE still pose: top of a small jump. Both knees gently bent, compact feet below the hips, hands balanced slightly outward at waist level. Head and chest stay solid and uncompressed.',
        'fall': 'ONE still pose: descent before landing. Extend both feet downward underneath the hips, bend the elbows a little outward for balance. Do not elongate the arms or torso.',
        'land': 'ONE still pose: landing absorption. Both soles planted on the same baseline, knees bent slightly, hands settle beside the hips. Lower the solid upper body by bending legs, without squeezing the head or chest.',
        'boost': 'ONE still pose: airborne second jump impulse. Both small knees fold underneath, elbows softly bent and both round hands outward for balance. No somersault, no spin, no new costume.',
    },
    'actions': {
        'windup': 'ONE still pose: windup for a rear-arm punch to the right. Rotate the waist and rear shoulder slightly away, draw the rear hand back close to the hip, keep the front hand low. Feet planted; connected compact arms.',
        'strike': 'ONE still pose: rear-arm punch to the right with a small waist rotation driving the shoulder. The rear hand extends forward at lower chest height, front hand stays near the opposite hip. Keep the reach plausible for the original short arms; no added boxing gloves.',
        'recoil': 'ONE still pose: pulling the rear fist back after a punch. Waist and shoulder settle halfway toward the original neutral pose, elbows bent, two hands present, soles planted.',
        'dashload': 'ONE still pose: a restrained rightward dash preparation. Slight knee bend, head and chest lean forward together, both small hands tucked close to the sides, stable original proportions.',
        'dashtravel': 'ONE still pose: rightward dash travel. The solid upper body leans gently forward, rear arm trails bent beside the hip, front arm bent low, one foot reaching slightly forward and the other trailing. Keep original short limbs.',
        'dashbrake': 'ONE still pose: rightward dash braking. Front foot planted under the body, rear foot catching up, two hands relax beside the hips, upper body returning upright.',
    },
    'support': {
        'pushside': 'ONE still pose: push an unseen box to the right with BOTH hands at its left face, elbows softly bent and palms at lower chest and waist height. Slight forward lean and short planted steps. No box drawn.',
        'pushup': 'ONE still pose: back view pushing an unseen box upward away from camera with BOTH round hands above the shoulders. Use the same shell, ear caps and compact proportions viewed from behind. Two feet grounded. No box drawn.',
        'pushdown': 'ONE still pose: facing camera and pushing an unseen box downward toward camera. BOTH round hands rest in front at hip height with compact bent elbows. Knees slightly bent; both feet visible at sides. No box drawn.',
        'hurt': 'ONE still pose: a small hit recoil. Solid upper body tilts backward slightly, both round hands loosen beside the hips, one foot bracing backward. Both arms attached and visible.',
    },
}

def main():
    ART.mkdir(parents=True, exist_ok=True)
    im = Image.open(BASE).convert('RGBA')
    im.save(ART / 'canonical-native.png')
    im.resize((1024, 1024), Image.Resampling.NEAREST).save(ART / 'canonical-reference-16x.png')
    contract = {
        'reference': BASE.relative_to(ROOT).as_posix(),
        'sha256': hashlib.sha256(BASE.read_bytes()).hexdigest(),
        'canvas': [64,64], 'groundPivot': [32,56],
        'identity': 'The approved native original is the only identity/style source. No generated high-resolution pose may become a replacement identity anchor.',
        'hands': 'Original compact round fingerless hands. No fingers, thumb, mitten spur, glove enlargement or disappearing hands.',
        'conversion': 'sprite-gen canonical component extraction and pixel-unfake, one complete single-pose source per state; native trace cleanup recorded separately. No region-specific rescale or rectangular head/chest patch overwrite.',
        'preserved': ['original relaxed Idle', 'approved Walk 14 frames', 'all V8/V9 history'],
        'motionGate': 'Review complete native frames and actual runtime movement. Clean alpha/identity alone cannot certify natural motion.',
    }
    (ART / 'identity-contract.json').write_text(json.dumps(contract, ensure_ascii=False, indent=2), encoding='utf-8')
    for group, poses in POSES.items():
        run = ART / group
        run.mkdir(exist_ok=True)
        request = {
            'cell': {'width':64, 'height':64, 'safe_margin_x':4, 'safe_margin_y':8},
            'states': {name: {'frames':1, 'fps':1, 'loop':False, 'action':action + ' The attached original native sprite alone defines the design, proportions, face, colors and pixel density. Both hands are fingerless round endcaps.'} for name, action in poses.items()},
            'fit': {'pixel_unfake':True, 'logical_height':64, 'palette_size':13, 'align_x':'alpha-centroid', 'align_y':'bottom', 'ground_frames':False, 'detail_bias':True, 'outline':False},
        }
        (run / 'request-input.json').write_text(json.dumps(request, indent=2), encoding='utf-8')
        colors = [list(c[:3]) for c, _ in Counter(c for c in im.getdata() if c[3]).most_common()]
        palette_path = run / 'palette.lock.json'
        if palette_path.exists() and not (run / 'first-generated-palette.json').exists():
            (run / 'first-generated-palette.json').write_bytes(palette_path.read_bytes())
        palette_path.write_text(json.dumps({'kind':'sprite-gen-palette-lock', 'source':'approved original Idle/00.png; shared across all poses', 'colors':colors}, indent=2), encoding='utf-8')
    print(ART)

if __name__ == '__main__': main()
