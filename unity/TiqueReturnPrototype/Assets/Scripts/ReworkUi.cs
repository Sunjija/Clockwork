using System;
using System.Collections.Generic;
using UnityEngine;
namespace TiqueReturn
{
    public sealed partial class ReworkGame
    {
        [Serializable] sealed class FontAtlas {public string characters="";public int columns=32,cell=16;}
        [Serializable] sealed class UiSkinInfo {public string name="";public int width=0,height=0;public int[] margins=Array.Empty<int>();}
        [Serializable] sealed class UiSkinFile {public UiSkinInfo[] skins=Array.Empty<UiSkinInfo>();}
        FontAtlas glyphs;Texture2D fontAtlas;
        readonly Dictionary<int,Texture2D> sizedFontAtlases=new Dictionary<int,Texture2D>();
        readonly Dictionary<char,int> glyphIndex=new Dictionary<char,int>();
        readonly Dictionary<string,Texture2D> uiTextures=new Dictionary<string,Texture2D>();
        readonly Dictionary<string,UiSkinInfo> uiSkins=new Dictionary<string,UiSkinInfo>();
        readonly UiPreferences uiPreferences=new UiPreferences();
        AdaptiveGuidance guidance=new AdaptiveGuidance();
        int menuSelection;Journey menuPhase;bool menuWasPaused;
        int pressedButton=-1;float pressedAt=-10;

        void ResetPuzzleGuide()
        {guidance=new AdaptiveGuidance();guidance.Observe(Model,ReworkCommand.Empty);}
        void LoadPixelUi()
        {
            string root=Resources.Load<TextAsset>("ReturnV2/UiV2/font")!=null?"ReturnV2/UiV2/":"ReturnV2/Feedback/";
            glyphs=JsonUtility.FromJson<FontAtlas>(Resources.Load<TextAsset>(root+"font").text);
            fontAtlas=Resources.Load<Texture2D>(root+"font");fontAtlas.filterMode=FilterMode.Point;
            // NeoDunggeunmo is a 16px-grid font. Smaller rasterizations lose
            // Korean strokes; retain the licensed original and scale only by
            // whole pixels. Historical candidate atlases are not loaded.
            sizedFontAtlases.Clear();
            if(glyphs.cell!=16)throw new InvalidOperationException("Expected native 16px UI font");
            glyphIndex.Clear();for(int i=0;i<glyphs.characters.Length;i++)glyphIndex[glyphs.characters[i]]=i;
            var skinFile=Resources.Load<TextAsset>("ReturnV2/UiV2/skins");
            if(skinFile!=null)foreach(var skin in JsonUtility.FromJson<UiSkinFile>(skinFile.text).skins)
            {
                uiSkins[skin.name]=skin;var texture=Resources.Load<Texture2D>("ReturnV2/UiV2/"+skin.name+"/00");
                if(texture==null)throw new InvalidOperationException("Missing compact UI skin: "+skin.name);
                texture.filterMode=FilterMode.Point;uiTextures[skin.name]=texture;
            }
            Debug.Log("COMPACT_UI_ROOT "+root+" glyphs="+glyphs.characters.Length+" skins="+uiTextures.Count);
        }
        Color UiColor(string name)
        {
            switch(name){case "dim":return dim;case "cyan":return cyan;case "gold":return gold;
                case "red":return red;case "shade":return new Color(.02f,.035f,.05f,.82f);default:return ink;}
        }
        void UiText(UiElement item,int offsetY=0,Color? color=null)
        {
            int x=item.x,y=item.y+offsetY;GUI.color=color??UiColor(item.color);
            if(item.size<glyphs.cell||item.size%glyphs.cell!=0)
                throw new InvalidOperationException("UI font requires integer native-pixel scale: "+item.size);
            var atlas=fontAtlas;int cell=glyphs.cell;
            // The pure layout already wraps with the same integer advances. These
            // are unchanged licensed glyph shapes, not generated lettering.
            foreach(char c in item.text)
            {
                if(c=='\n'){x=item.x;y+=item.size+2;continue;}
                if(glyphIndex.TryGetValue(c,out int index))
                    GUI.DrawTextureWithTexCoords(new Rect(x,y,item.size,item.size),atlas,
                        new Rect(index%glyphs.columns*(float)cell/atlas.width,
                            1-(index/glyphs.columns+1)*(float)cell/atlas.height,
                            (float)cell/atlas.width,(float)cell/atlas.height),true);
                else if(c!=' ')Debug.LogError("Missing compact UI glyph: "+c);
                x+=c<128?item.size/2:item.size;
            }
            GUI.color=Color.white;
        }
        void UiFrame(string name,Rect rect)
        {
            Texture2D tex;int[] margins;
            if(uiTextures.TryGetValue(name,out tex))margins=uiSkins[name].margins;
            else{tex=animations["fx-"+name][0].texture;margins=new[]{3,3,3,3};}
            int left=Math.Min(margins[0],(int)rect.width/2),right=Math.Min(margins[2],(int)rect.width-left);
            int top=Math.Min(margins[1],(int)rect.height/2),bottom=Math.Min(margins[3],(int)rect.height-top);
            float[] dx={rect.x,rect.x+left,rect.xMax-right,rect.xMax};
            float[] dy={rect.y,rect.y+top,rect.yMax-bottom,rect.yMax};
            int[] sx={0,left,tex.width-right,tex.width},sy={0,top,tex.height-bottom,tex.height};
            GUI.color=Color.white;
            // Nine-slice directly samples the generated native frame. Corners
            // remain intact; Point sampling avoids smoothed decoration.
            for(int row=0;row<3;row++)for(int col=0;col<3;col++)
            {
                float w=dx[col+1]-dx[col],h=dy[row+1]-dy[row];if(w<=0||h<=0)continue;
                int sw=sx[col+1]-sx[col],sh=sy[row+1]-sy[row];
                if((row==1)!=(col==1))
                {
                    // Native edge strips tile and crop at the final pixel,
                    // rather than stretching a small rivet into a long mark.
                    for(int ty=0;ty<h;ty+=sh)for(int tx=0;tx<w;tx+=sw)
                    {
                        int cw=Math.Min(sw,(int)w-tx),ch=Math.Min(sh,(int)h-ty);
                        GUI.DrawTextureWithTexCoords(new Rect(dx[col]+tx,dy[row]+ty,cw,ch),tex,
                            new Rect((float)sx[col]/tex.width,1-(float)(sy[row]+ch)/tex.height,
                                (float)cw/tex.width,(float)ch/tex.height),true);
                    }
                }
                else GUI.DrawTextureWithTexCoords(new Rect(dx[col],dy[row],w,h),tex,
                    new Rect((float)sx[col]/tex.width,1-(float)sy[row+1]/tex.height,
                        (float)sw/tex.width,(float)sh/tex.height),true);
            }
        }
        void FlushInput(bool release=true)
        {pending=ReworkCommand.Empty;accumulator=0;heldDirection=-1;keyRepeat=0;releaseGate=release;}
        void RunUiAction(string action)
        {
            var m=Model;
            switch(action)
            {
                case "continue":m.paused=false;FlushInput();break;
                case "toggle-mute":m.muted=!m.muted;break;
                case "toggle-effects":m.reducedEffects=!m.reducedEffects;break;
                case "toggle-auto-help":uiPreferences.autoHelp=!uiPreferences.autoHelp;break;
                case "toggle-large-text":uiPreferences.largeText=!uiPreferences.largeText;break;
                case "restart-combat":if(m.RestartCombat())FlushInput();break;
                case "restart-all":Restart();break;
                case "quit":Application.Quit();break;
                case "start":m.Start();FlushInput();break;
                case "retry":m.Retry();FlushInput();break;
                case "toggle-assisted":m.assisted=!m.assisted;break;
                case "undo":pending.undo=true;break;
                case "restart-room":pending.restart=true;break;
                case "next":pending.interact=true;break;
            }
        }
        void MenuAction(int selected)
        {
            var plan=CompactUiLayout.Build(Model,uiPreferences,guidance.Message,guidance.Visible);
            foreach(var item in plan.elements)if(item.kind=="button"&&item.index==selected&&item.enabled)
            {RunUiAction(item.action);return;}
        }
        bool HandleMenuKeys()
        {
            var m=Model;if(menuPhase!=m.phase||menuWasPaused!=m.paused)
            {menuSelection=0;pressedButton=-1;menuPhase=m.phase;menuWasPaused=m.paused;}
            bool menu=m.paused||m.phase==Journey.Title||m.phase==Journey.Dead||m.phase==Journey.Ending;
            if(!menu)
            {
                if(m.phase==Journey.Puzzle)
                {
                    if(Input.GetKeyDown(KeyCode.Tab))menuSelection=(menuSelection+1)%2;
                    if(Input.GetKeyDown(KeyCode.Return)){if(menuSelection==0)pending.undo=true;else pending.restart=true;}
                }
                return false;
            }
            int count=CompactUiLayout.MenuCount(m);
            if(Input.GetKeyDown(KeyCode.DownArrow)||Input.GetKeyDown(KeyCode.Tab))menuSelection=(menuSelection+1)%count;
            if(Input.GetKeyDown(KeyCode.UpArrow))menuSelection=(menuSelection+count-1)%count;
            if(Input.GetKeyDown(KeyCode.Return))MenuAction(menuSelection);
            return true;
        }
        void OnGUI()
        {
            if(Model==null||target==null||glyphs==null)return;
            int scale=Math.Max(1,Math.Min(Screen.width/640,Screen.height/360));
            int ox=(Screen.width-640*scale)/2,oy=(Screen.height-360*scale)/2;
            GUI.matrix=Matrix4x4.TRS(new Vector3(ox,oy,0),Quaternion.identity,new Vector3(scale,scale,1));
            GUI.color=Color.white;GUI.DrawTexture(new Rect(0,0,640,360),target,ScaleMode.StretchToFill,false);
            var plan=CompactUiLayout.Build(Model,uiPreferences,uiReview?uiReviewHelp:guidance.Message,
                uiReview?uiReviewHelp.Length>0:guidance.Visible);
            foreach(var item in plan.elements)
            {
                var rect=new Rect(item.x,item.y,item.width,item.height);
                if(item.kind=="panel")UiFrame(item.asset.Length>0?item.asset:"panel",rect);
                else if(item.kind=="fill")
                {GUI.color=UiColor(item.color);GUI.DrawTexture(rect,Texture2D.whiteTexture);GUI.color=Color.white;}
                else if(item.kind=="text")UiText(item);
                else if(item.kind=="image")
                {
                    if(!animations.TryGetValue(item.asset,out var frames))throw new InvalidOperationException("Missing UI reuse asset: "+item.asset);
                    GUI.color=string.IsNullOrEmpty(item.color)||item.color=="ink"?Color.white:UiColor(item.color);
                    GUI.DrawTexture(rect,frames[0].texture,ScaleMode.StretchToFill,true);GUI.color=Color.white;
                }
                else if(item.kind=="button")
                {
                    bool over=!uiReview&&rect.Contains(Event.current.mousePosition);
                    if(!uiReview&&item.enabled&&over&&Event.current.type==EventType.MouseDown&&Event.current.button==0)
                    {pressedButton=item.index;pressedAt=Time.unscaledTime;menuSelection=item.index;}
                    bool pressed=item.enabled&&pressedButton==item.index&&Time.unscaledTime-pressedAt<.1f;
                    string skin=!item.enabled?"button-disabled":pressed?"button-pressed":over||menuSelection==item.index?"button-selected":"button";
                    UiFrame(skin,rect);
                    UiText(new UiElement{x=item.x+12,y=item.y+(item.height-item.size)/2,width=item.width-24,
                        height=item.height,text=item.text,size=item.size,color=item.enabled?"ink":"dim"},pressed?1:0);
                    if(!uiReview&&item.enabled&&over&&Event.current.type==EventType.MouseUp&&Event.current.button==0&&pressedButton==item.index)
                    {Event.current.Use();pressedButton=-1;RunUiAction(item.action);break;}
                }
            }
            if(Event.current.type==EventType.MouseUp&&Event.current.button==0)pressedButton=-1;
            GUI.color=Color.white;
        }
    }
}
