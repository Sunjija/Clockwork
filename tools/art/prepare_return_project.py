"""Author saved scene/import settings from this repository's Unity 6000.5 templates.

Does not run Unity or validate serialization in the editor.
"""
from pathlib import Path
import hashlib, re, json

repo=Path(__file__).resolve().parents[2]
root=repo/'unity/TiqueReturnPrototype'
original=repo/'unity/ClockworkPrototype'
def guid(path):return hashlib.sha256(('TiqueReturn/'+str(path).replace('\\','/')).encode()).hexdigest()[:32]
settings=(original/'ProjectSettings/ProjectSettings.asset').read_text(encoding='utf8')
for key,value in {'productGUID':guid('player'),'companyName':'Clockwork','productName':'Tique Return','activeInputHandler':'0','resizableWindow':'1','bundleVersion':'0.1.0','fullscreenMode':'3'}.items():
    settings=re.sub(r'(?m)^  '+key+r':.*$', '  '+key+': '+value,settings)
settings=settings.replace('  scriptingBackend: {}','  scriptingBackend:\n    Standalone: 0')
(root/'ProjectSettings/ProjectSettings.asset').write_text(settings,encoding='utf8')
graphics=(original/'ProjectSettings/GraphicsSettings.asset').read_text(encoding='utf8')
graphics=re.sub(r'(?m)^  m_CustomRenderPipeline:.*$', '  m_CustomRenderPipeline: {fileID: 0}',graphics)
graphics=re.sub(r'  m_RenderPipelineGlobalSettingsMap:\n    [^\n]+\n','  m_RenderPipelineGlobalSettingsMap: {}\n',graphics)
(root/'ProjectSettings/GraphicsSettings.asset').write_text(graphics,encoding='utf8')
scenePath='Assets/Scenes/TiqueReturn.unity'
scene=root/scenePath;scene.parent.mkdir(parents=True,exist_ok=True)
# Only engine defaults; no original level objects or original project asset GUIDs.
preamble=(original/'Assets/Clockwork/Scenes/CombatLab.unity').read_text(encoding='utf8').split('--- !u!1 &')[0]
scene.write_text(preamble+'''--- !u!1 &1000
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  serializedVersion: 6
  m_Component:
  - component: {fileID: 1001}
  - component: {fileID: 1002}
  m_Layer: 0
  m_Name: Tique Return - Game
  m_TagString: Untagged
  m_Icon: {fileID: 0}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &1001
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: 1000}
  serializedVersion: 2
  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}
  m_LocalPosition: {x: 0, y: 0, z: 0}
  m_LocalScale: {x: 1, y: 1, z: 1}
  m_ConstrainProportionsScale: 0
  m_Children: []
  m_Father: {fileID: 0}
  m_LocalEulerAnglesHint: {x: 0, y: 0, z: 0}
--- !u!114 &1002
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: 1000}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {fileID: 11500000, guid: '''+guid('Assets/Scripts/ReturnGame.cs')+''', type: 3}
  m_Name:
  m_EditorClassIdentifier:
--- !u!1660057539 &9223372036854775807
SceneRoots:
  m_ObjectHideFlags: 0
  m_Roots:
  - {fileID: 1001}
''',encoding='utf8')
(root/'ProjectSettings/EditorBuildSettings.asset').write_text('''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!1045 &1
EditorBuildSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_Scenes:
  - enabled: 1
    path: '''+scenePath+'''
    guid: '''+guid(scenePath)+'''
  m_configObjects: {}
''',encoding='utf8')
pngTemplate=(original/'Assets/Clockwork/QA/caligo-unity-preview.png.meta').read_text(encoding='utf8')
for before,after in [('enableMipMap: 1','enableMipMap: 0'),('filterMode: 1','filterMode: 0'),('maxTextureSize: 2048','maxTextureSize: 1024'),('nPOTScale: 1','nPOTScale: 0'),('spritePixelsToUnits: 100','spritePixelsToUnits: 64'),('alphaIsTransparency: 0','alphaIsTransparency: 1'),('textureCompression: 1','textureCompression: 0'),('wrapU: 0','wrapU: 1'),('wrapV: 0','wrapV: 1'),('wrapW: 0','wrapW: 1')]:
    pngTemplate=pngTemplate.replace(before,after)
audioTemplate=(original/'Assets/Clockwork/ThirdParty/Curated/Audio/UI/switch1.ogg.meta').read_text(encoding='utf8').replace('compressionFormat: 1','compressionFormat: 0').replace('preloadAudioData: 0','preloadAudioData: 1').replace('normalize: 1','normalize: 0').replace('3D: 1','3D: 0')
for p in sorted((root/'Assets').rglob('*')):
    if p.suffix=='.meta':continue
    rel=p.relative_to(root).as_posix()
    header='fileFormatVersion: 2\nguid: '+guid(rel)+'\n'
    if p.is_dir():body=header+'folderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    elif p.suffix=='.png':body=re.sub('guid: [0-9a-f]{32}','guid: '+guid(rel),pngTemplate,count=1)
    elif p.suffix=='.wav':body=re.sub('guid: [0-9a-f]{32}','guid: '+guid(rel),audioTemplate,count=1)
    elif p.suffix=='.cs':body=header+'MonoImporter:\n  externalObjects: {}\n  serializedVersion: 2\n  defaultReferences: []\n  executionOrder: 0\n  icon: {fileID: 0}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    else:body=header+('TextScriptImporter' if p.suffix=='.json' else 'DefaultImporter')+':\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    Path(str(p)+'.meta').write_text(body,encoding='utf8')
(root/'QA/validation-status.json').write_text(json.dumps({
    'unityVersion':'6000.5.3f1','unityEditorImport':'NOT_RUN','unityPlayerBuild':'BLOCKED','unityRuntimeSmoke':'NOT_RUN',
    'blocker':'Unity exited with code 198: No valid Unity Editor license found. User cannot activate currently.',
    'sourceCompile':'PASS; see source-compile.json','productionModel':'PASS; see model-checks.json',
    'screenshots':'None from Unity. layout-study.png is an offline layout study only.',
    'readyForExhibition':False},indent=2),encoding='utf8')
print('Saved scene, deterministic metadata, project settings and explicit QA status.')
