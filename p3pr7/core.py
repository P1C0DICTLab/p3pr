import json
import numbers
import webbrowser
import tempfile
import os
from typing import Optional, Union, List, Dict, Any, Iterable

# =============================================================================
# 核心类
# =============================================================================
class Scene:
    """
    点云场景，用于构建数据并导出为独立的 HTML 查看器。
    """

    _HTML_TEMPLATE = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"/><meta name="viewport"content="width=device-width, initial-scale=1.0"/><title>3PR专用查看器</title><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#111;overflow:hidden;user-select:none;font-family:'Segoe UI',Arial,sans-serif}canvas{display:block}#title{position:fixed;top:20px;left:50%;transform:translateX(-50%);z-index:30;color:#fff;font-size:28px;font-weight:300;letter-spacing:4px;text-shadow:0 0 30px rgba(0,0,0,0.9),0 4px 12px rgba(0,0,0,0.5);background:rgba(0,0,0,0.3);padding:8px 28px;border-radius:40px;backdrop-filter:blur(4px);border:1px solid rgba(255,255,255,0.08);pointer-events:none;display:none}#legend{position:fixed;bottom:30px;right:30px;z-index:20;background:rgba(10,10,25,0.75);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.10);border-radius:12px;padding:12px 18px;min-width:140px;color:#d0d8e8;font-size:13px;box-shadow:0 8px 32px rgba(0,0,0,0.6);pointer-events:none;display:none}#legend.legend-title{font-weight:600;font-size:14px;margin-bottom:6px;color:#aac;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:4px}.legend-item{display:flex;align-items:center;margin:4px 0;gap:10px}.legend-swatch{display:inline-block;width:14px;height:14px;border-radius:4px;border:1px solid rgba(255,255,255,0.15);flex-shrink:0}.legend-label{color:#d0d8e8;font-weight:400}#panel{position:fixed;top:14px;left:16px;z-index:10;min-width:180px;padding:10px 16px;color:#c8d0e0;font-size:13px;font-weight:400;line-height:1.6;letter-spacing:0.2px;background:rgba(10,10,20,0.7);border:1px solid rgba(255,255,255,0.08);border-radius:10px;backdrop-filter:blur(6px);box-shadow:0 4px 20px rgba(0,0,0,0.5);pointer-events:none}#panel.fps-line{font-weight:600;color:#8cf;font-size:14px;margin-bottom:2px}#panel.fps-line span{color:#aaf}#panel.fps-line.status{color:#8f8;font-size:12px;font-weight:400}#panel.param-line{color:#b0bcdb;font-size:12.5px}#panel.param-line span{color:#e0e8ff;font-weight:500}#panel.param-line.label{color:#8899bb;margin-right:2px}#panel.param-line.value{color:#e0e8ff;font-weight:500}#panel.sub-line{font-size:11px;color:#667}#panel.sub-line.label{color:#8899bb}#panel.sub-line.value{color:#aac}#hover-panel{position:fixed;top:20px;right:20px;z-index:20;max-width:320px;padding:12px 16px;color:#e0e8ff;font-size:13px;line-height:1.5;background:rgba(8,8,20,0.85);border:1px solid rgba(255,255,255,0.12);border-radius:10px;backdrop-filter:blur(8px);box-shadow:0 6px 24px rgba(0,0,0,0.7);pointer-events:none;display:none;transition:opacity 0.15s ease}#hover-panel.title{font-weight:600;color:#8cf;font-size:14px;margin-bottom:4px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:4px}#hover-panel.prop{display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.04)}#hover-panel.prop-key{color:#8899bb}#hover-panel.prop-value{color:#e0e8ff;font-weight:500;text-align:right;word-break:break-all}#hover-panel.coord{margin-top:6px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.1);font-size:12px;color:#aac}#hover-panel.coord span{color:#c8d0e0}#info{position:fixed;bottom:18px;left:18px;z-index:10;padding:5px 14px;color:#aaa;font-size:13px;background:rgba(0,0,0,0.45);border:1px solid rgba(255,255,255,0.05);border-radius:6px;backdrop-filter:blur(2px);pointer-events:none}#info kbd{padding:0 6px;color:#ddd;font-size:12px;background:rgba(255,255,255,0.08);border-radius:3px}</style></head><body><div id="title">3PR查看器</div><div id="legend"><div class="legend-title">图例</div></div><div id="panel"><div class="fps-line">⚡<span id="fps-value">--</span>FPS</div><div class="fps-line"style="font-weight:400;font-size:12px;color:#aac;">MEM<span id="mem-used">--</span>/<span id="mem-total">--</span>MB<span id="mem-percent"style="color:#88aaff;">(--%)</span></div><div class="fps-line"style="font-weight:400;font-size:12px;color:#aac;">Time<span id="frame-time">--</span>ms/帧<span id="gc-indicator"style="color:#88ff88;">⚡</span></div><div class="fps-line"style="font-weight:400;font-size:12px;color:#aac;"><span class="status"id="render-status">⚪空闲</span></div><div class="param-line"><span class="label">θ</span><span class="value"id="fps-theta">0.0</span>°<span class="label"style="margin-left:10px;">φ</span><span class="value"id="fps-phi">0.0</span>°</div><div class="param-line"><span class="label">距离</span><span class="value"id="fps-dist">0.0</span></div><div class="param-line"><span class="label">焦点</span>(<span class="value"id="fps-tx">0.0</span>,<span class="value"id="fps-ty">0.0</span>,<span class="value"id="fps-tz">0.0</span>)</div><div class="sub-line"><span class="label">点总数</span><span class="value"id="point-count">0</span><span class="label"style="margin-left:8px;">已绘</span><span class="value"id="drawn-count">0</span></div></div><div id="hover-panel"><div class="title"id="hover-title">📍点信息</div><div id="hover-body"></div><div class="coord"id="hover-coord"></div></div><div id="info">左键旋转·滚轮缩放·右键平移·<kbd>W A S D Q E</kbd>焦点平移·<kbd>R</kbd>重置</div><script>window.__EMBEDDED_DATA__=__DATA_PLACEHOLDER__;</script><script>const RENDER_CONFIG={FOCAL:600,MAX_RENDER_POINTS:1000000,BATCH_SIZE:10000,PREVIEW_COUNT:2000,PREVIEW_THRESHOLD:10000,IDLE_DELAY:300,FULL_RENDER_DELAY:300,DISTANCE_MIN:1,DISTANCE_MAX:300,ROTATION_SPEED:0.010,PAN_SPEED:0.0035,ZOOM_SPEED:1.05,KEY_PAN_SPEED:0.02,};const DEFAULT_CONFIG={title:'3PR 查看器',background:'#18182a',camera:{distance:25,theta:0.5,phi:0.4,target:[0,0,0]},axis:{enabled:true,x:{label:'X轴',color:'#ff5555'},y:{label:'Y轴',color:'#55ff55'},z:{label:'Z轴',color:'#5588ff'},leftHanded:false,length:500,},legend:[],};let testPoints=[];let sortedPoints=[];let previewSorted=[];let drawIndex=0;let isPreviewMode=false;let needsReSort=true;let forceFullRender=false;let needsRender=false;let isRendering=false;let idleTimer=null;let fullRenderTimer=null;let mouseX=-9999,mouseY=-9999;let needsPick=false;let hoveredPointIndex=-1;let lastMemSize=0;let sceneBackground='#18182a';let config=null;const DOM={fps:document.getElementById('fps-value'),theta:document.getElementById('fps-theta'),phi:document.getElementById('fps-phi'),dist:document.getElementById('fps-dist'),tx:document.getElementById('fps-tx'),ty:document.getElementById('fps-ty'),tz:document.getElementById('fps-tz'),memUsed:document.getElementById('mem-used'),memTotal:document.getElementById('mem-total'),memPercent:document.getElementById('mem-percent'),frameTime:document.getElementById('frame-time'),gcIndicator:document.getElementById('gc-indicator'),renderStatus:document.getElementById('render-status'),pointCount:document.getElementById('point-count'),drawnCount:document.getElementById('drawn-count'),hoverPanel:document.getElementById('hover-panel'),hoverTitle:document.getElementById('hover-title'),hoverBody:document.getElementById('hover-body'),hoverCoord:document.getElementById('hover-coord'),};function deepMerge(target,source){const result={...target};for(const key in source){if(source[key]&&typeof source[key]==='object'&&!Array.isArray(source[key])){result[key]=deepMerge(target[key]||{},source[key])}else{result[key]=source[key]}}return result}function parseColor(color){if(typeof color==='string'){let c=color.trim();if(c.startsWith('#')){c=c.slice(1);if(c.length===3){const r=parseInt(c[0]+c[0],16)/255;const g=parseInt(c[1]+c[1],16)/255;const b=parseInt(c[2]+c[2],16)/255;return[r,g,b]}else if(c.length===6){const r=parseInt(c.slice(0,2),16)/255;const g=parseInt(c.slice(2,4),16)/255;const b=parseInt(c.slice(4,6),16)/255;return[r,g,b]}}throw new Error('Unsupported color string: '+color);}if(Array.isArray(color)&&color.length===3){if(color.some(v=>v>1))return color.map(v=>v/255);return color.slice()}return[1,1,1]}const Vec={sub:(a,b)=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]],dot:(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2],cross:(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],normalize:(v)=>{const len=Math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]);return len>0?[v[0]/len,v[1]/len,v[2]/len]:[0,0,0]},scale:(v,s)=>[v[0]*s,v[1]*s,v[2]*s],add:(a,b)=>[a[0]+b[0],a[1]+b[1],a[2]+b[2]],};function createOrbitCamera(opts){const target=opts.target||[0,0,0];const distance=opts.distance||10;const theta=opts.theta||0;const phi=opts.phi||Math.PI/4;const up=opts.up||[0,1,0];return{target:target.slice(),distance,theta,phi,up:up.slice(),tick(){const cosPhi=Math.cos(this.phi);const sinPhi=Math.sin(this.phi);const cosTheta=Math.cos(this.theta);const sinTheta=Math.sin(this.theta);const pos=[this.target[0]+this.distance*cosPhi*sinTheta,this.target[1]+this.distance*sinPhi,this.target[2]+this.distance*cosPhi*cosTheta,];const forward=Vec.normalize(Vec.sub(this.target,pos));const right=Vec.normalize(Vec.cross(forward,this.up));const camUp=Vec.normalize(Vec.cross(right,forward));return{position:pos,right,up:camUp,forward}}}}let camera=createOrbitCamera({target:[0,0,0],distance:25,theta:0.5,phi:0.4,up:[0,1,0]});function worldToCamera(worldPos,view){const rel=Vec.sub(worldPos,view.position);return{x:Vec.dot(rel,view.right),y:Vec.dot(rel,view.up),z:Vec.dot(rel,view.forward)}}function project(camCoord,focal){if(camCoord.z<=0.001)return null;const scale=focal/camCoord.z;return{x:camCoord.x*scale,y:camCoord.y*scale,depth:camCoord.z}}const canvas=document.createElement('canvas');document.body.prepend(canvas);const ctx=canvas.getContext('2d');let canvasWidth=0,canvasHeight=0;function resizeCanvas(){canvasWidth=window.innerWidth;canvasHeight=window.innerHeight;canvas.width=canvasWidth*devicePixelRatio;canvas.height=canvasHeight*devicePixelRatio;canvas.style.width=canvasWidth+'px';canvas.style.height=canvasHeight+'px';ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);scheduleRender()}window.addEventListener('resize',resizeCanvas);function drawShape(ctx,x,y,radius,color,shape){const[r,g,b]=parseColor(color);ctx.fillStyle=`rgb(${r*255|0},${g*255|0},${b*255|0})`;ctx.strokeStyle='rgba(255,255,255,0.35)';ctx.lineWidth=0.5;ctx.beginPath();switch(shape){case'square':{const half=radius*0.8;ctx.rect(x-half,y-half,half*2,half*2);break}case'triangle':{for(let i=0;i<3;i++){const angle=-Math.PI/2+(i*2*Math.PI/3);const px=x+radius*Math.cos(angle);const py=y+radius*Math.sin(angle);i===0?ctx.moveTo(px,py):ctx.lineTo(px,py)}ctx.closePath();break}case'diamond':{ctx.moveTo(x,y-radius);ctx.lineTo(x+radius,y);ctx.lineTo(x,y+radius);ctx.lineTo(x-radius,y);ctx.closePath();break}case'star':{const outer=radius,inner=radius*0.45;const points=5;for(let i=0;i<points*2;i++){const r2=i%2===0?outer:inner;const angle=-Math.PI/2+(i*Math.PI)/points;const px=x+r2*Math.cos(angle);const py=y+r2*Math.sin(angle);i===0?ctx.moveTo(px,py):ctx.lineTo(px,py)}ctx.closePath();break}case'cross':{const w=radius*0.25,len=radius*1.2;ctx.rect(x-w/2,y-len/2,w,len);ctx.rect(x-len/2,y-w/2,len,w);break}default:{ctx.arc(x,y,radius,0,2*Math.PI)}}ctx.fill();ctx.stroke()}function drawAxesAndClear(view){const cx=canvasWidth/2;const cy=canvasHeight/2;ctx.fillStyle=sceneBackground;ctx.fillRect(0,0,canvasWidth,canvasHeight);const axisEnabled=(config&&config.axis&&config.axis.enabled!==undefined)?config.axis.enabled:true;if(!axisEnabled)return;const axCfg=(config&&config.axis)?config.axis:{};const origin=[0,0,0];const axisDefs=[{dir:[1,0,0],color:parseColor(axCfg.x?.color||'#ff5555'),label:axCfg.x?.label||'X'},{dir:[0,1,0],color:parseColor(axCfg.y?.color||'#55ff55'),label:axCfg.y?.label||'Y'},{dir:[0,0,axCfg.leftHanded?-1:1],color:parseColor(axCfg.z?.color||'#5588ff'),label:axCfg.z?.label||'Z'},];const axisLen=axCfg.length||500;const distToTarget=camera.distance;const tickSpacingWorld=Math.pow(10,Math.floor(Math.log10(Math.max(1,distToTarget/5))));const tickLength=0.6;for(const ax of axisDefs){const dir=ax.dir;const pPos=[origin[0]+dir[0]*axisLen,origin[1]+dir[1]*axisLen,origin[2]+dir[2]*axisLen];const pNeg=[origin[0]-dir[0]*axisLen,origin[1]-dir[1]*axisLen,origin[2]-dir[2]*axisLen];const segPos=clipSegment(origin,pPos,view);if(segPos){ctx.beginPath();ctx.moveTo(cx+segPos.p1.x,cy-segPos.p1.y);ctx.lineTo(cx+segPos.p2.x,cy-segPos.p2.y);const[r,g,b]=ax.color;ctx.strokeStyle=`rgb(${r*255|0},${g*255|0},${b*255|0})`;ctx.lineWidth=2.5;ctx.stroke()}const segNeg=clipSegment(origin,pNeg,view);if(segNeg){const dark=ax.color.map(c=>c*0.4);ctx.beginPath();ctx.moveTo(cx+segNeg.p1.x,cy-segNeg.p1.y);ctx.lineTo(cx+segNeg.p2.x,cy-segNeg.p2.y);ctx.strokeStyle=`rgb(${dark[0]*255|0},${dark[1]*255|0},${dark[2]*255|0})`;ctx.lineWidth=1.5;ctx.stroke()}let d=tickSpacingWorld;while(d<axisLen){const pos=[origin[0]+dir[0]*d,origin[1]+dir[1]*d,origin[2]+dir[2]*d];let perpDir;if(Math.abs(dir[1])<0.9){perpDir=Vec.normalize(Vec.cross(dir,[0,1,0]))}else{perpDir=Vec.normalize(Vec.cross(dir,[1,0,0]))}const p1=[pos[0]-perpDir[0]*tickLength/2,pos[1]-perpDir[1]*tickLength/2,pos[2]-perpDir[2]*tickLength/2];const p2=[pos[0]+perpDir[0]*tickLength/2,pos[1]+perpDir[1]*tickLength/2,pos[2]+perpDir[2]*tickLength/2];const segTick=clipSegment(p1,p2,view);if(segTick){ctx.beginPath();ctx.moveTo(cx+segTick.p1.x,cy-segTick.p1.y);ctx.lineTo(cx+segTick.p2.x,cy-segTick.p2.y);ctx.strokeStyle='rgba(255,255,255,0.5)';ctx.lineWidth=1.0;ctx.stroke()}d+=tickSpacingWorld}}const labelX=12;const labelY=canvasHeight-120;const lineHeight=24;ctx.font='bold 15px Arial';ctx.textAlign='left';ctx.textBaseline='top';ctx.shadowColor='rgba(0,0,0,0.8)';ctx.shadowBlur=6;for(let i=0;i<axisDefs.length;i++){const ax=axisDefs[i];const[r,g,b]=ax.color;ctx.fillStyle=`rgb(${r*255|0},${g*255|0},${b*255|0})`;ctx.fillText(ax.label,labelX,labelY+i*lineHeight)}ctx.shadowBlur=0}function clipSegment(p1,p2,view){const focal=RENDER_CONFIG.FOCAL;const c1=worldToCamera(p1,view);const c2=worldToCamera(p2,view);if(c1.z<=0&&c2.z<=0)return null;if(c1.z>0&&c2.z>0){const proj1=project(c1,focal);const proj2=project(c2,focal);if(proj1&&proj2)return{p1:proj1,p2:proj2};return null}let pFront,pBack,cFront,cBack;if(c1.z>0){cFront=c1;cBack=c2;pFront=p1;pBack=p2}else{cFront=c2;cBack=c1;pFront=p2;pBack=p1}const t=cFront.z/(cFront.z-cBack.z);const interpWorld=[pFront[0]+t*(pBack[0]-pFront[0]),pFront[1]+t*(pBack[1]-pFront[1]),pFront[2]+t*(pBack[2]-pFront[2])];const projFront=project(cFront,focal);const interpCam=worldToCamera(interpWorld,view);interpCam.z=0.001;const projInterp=project(interpCam,focal);if(projFront&&projInterp)return{p1:projFront,p2:projInterp};return null}function sortPointsByDepth(points,view){const focal=RENDER_CONFIG.FOCAL;const maxPoints=Math.min(points.length,RENDER_CONFIG.MAX_RENDER_POINTS);const result=[];for(let i=0;i<maxPoints;i++){const pt=points[i];const camCoord=worldToCamera(pt.pos,view);const proj=project(camCoord,focal);if(proj){const cx=canvasWidth/2,cy=canvasHeight/2;const depthFactor=Math.max(0.3,1/(1+proj.depth*0.015));const radius=pt.size*depthFactor;const shape=pt.shape||pt.meta?.shape||'circle';result.push({proj,depth:proj.depth,color:pt.color,size:pt.size,meta:pt.meta||{},pos:pt.pos,shape,screenX:cx+proj.x,screenY:cy-proj.y,radius,})}}result.sort((a,b)=>b.depth-a.depth);return result}function renderFrame(){const view=camera.tick();if(needsReSort){needsReSort=false;drawAxesAndClear(view);if(isPreviewMode){const totalPoints=testPoints.length;const sampleSize=Math.min(totalPoints,RENDER_CONFIG.PREVIEW_COUNT);const step=Math.max(1,Math.floor(totalPoints/sampleSize));const previewPoints=[];for(let i=0;i<totalPoints&&previewPoints.length<sampleSize;i+=step){previewPoints.push(testPoints[i])}while(previewPoints.length<sampleSize&&previewPoints.length<totalPoints){previewPoints.push(testPoints[previewPoints.length])}previewSorted=sortPointsByDepth(previewPoints,view);drawIndex=0}else{sortedPoints=sortPointsByDepth(testPoints,view);drawIndex=0}}const cx=canvasWidth/2,cy=canvasHeight/2;if(isPreviewMode){for(let i=0;i<previewSorted.length;i++){const obj=previewSorted[i];drawShape(ctx,obj.screenX,obj.screenY,obj.radius,obj.color,obj.shape)}DOM.drawnCount.textContent=previewSorted.length}else{const end=Math.min(drawIndex+RENDER_CONFIG.BATCH_SIZE,sortedPoints.length);for(let i=drawIndex;i<end;i++){const obj=sortedPoints[i];drawShape(ctx,obj.screenX,obj.screenY,obj.radius,obj.color,obj.shape)}drawIndex=end;DOM.drawnCount.textContent=drawIndex}if(needsRender){if(isPreviewMode){isRendering=false;DOM.renderStatus.textContent='⚪ 空闲';if(idleTimer)clearTimeout(idleTimer);if(fullRenderTimer)clearTimeout(fullRenderTimer);idleTimer=setTimeout(()=>{idleTimer=null;fullRenderTimer=setTimeout(()=>{fullRenderTimer=null;isPreviewMode=false;needsReSort=true;needsRender=true;startRenderLoop()},RENDER_CONFIG.FULL_RENDER_DELAY)},RENDER_CONFIG.IDLE_DELAY);if(needsPick)performPick()}else{if(drawIndex<sortedPoints.length){requestAnimationFrame(renderFrame)}else{isRendering=false;DOM.renderStatus.textContent='⚪ 空闲';if(needsPick)performPick()}}}else{isRendering=false;DOM.renderStatus.textContent='⚪ 空闲';if(needsPick)performPick()}}function startRenderLoop(){if(!isRendering){isRendering=true;needsRender=true;DOM.renderStatus.textContent='🟢 渲染中';requestAnimationFrame(renderFrame)}}function scheduleRender(){const totalPoints=testPoints.length;if(forceFullRender){forceFullRender=false;isPreviewMode=false;needsReSort=true;needsRender=true;if(idleTimer)clearTimeout(idleTimer);if(fullRenderTimer)clearTimeout(fullRenderTimer);startRenderLoop();return}if(totalPoints<=RENDER_CONFIG.PREVIEW_THRESHOLD){isPreviewMode=false;needsReSort=true;needsRender=true;if(idleTimer)clearTimeout(idleTimer);if(fullRenderTimer)clearTimeout(fullRenderTimer);startRenderLoop();return}if(!isPreviewMode){isPreviewMode=true;needsReSort=true}needsRender=true;if(idleTimer)clearTimeout(idleTimer);if(fullRenderTimer)clearTimeout(fullRenderTimer);startRenderLoop()}function performPick(){needsPick=false;if(isRendering||(isPreviewMode&&drawIndex<previewSorted.length)||(!isPreviewMode&&drawIndex<sortedPoints.length)){return}const rect=canvas.getBoundingClientRect();const scaleX=canvasWidth/rect.width;const scaleY=canvasHeight/rect.height;const logicX=(mouseX-rect.left)*scaleX;const logicY=(mouseY-rect.top)*scaleY;let found=-1;const list=isPreviewMode?previewSorted:sortedPoints;for(let i=list.length-1;i>=0;i--){const obj=list[i];const dx=logicX-obj.screenX;const dy=logicY-obj.screenY;if(Math.sqrt(dx*dx+dy*dy)<=obj.radius){found=i;break}}if(found!==-1){const obj=list[found];const meta=obj.meta||{};let bodyHTML='';for(const[key,value]of Object.entries(meta)){bodyHTML+=`<div class="prop"><span class="prop-key">${key}</span><span class="prop-value">${value}</span></div>`}DOM.hoverBody.innerHTML=bodyHTML;const coordStr=`(${obj.pos[0].toFixed(3)},${obj.pos[1].toFixed(3)},${obj.pos[2].toFixed(3)})`;const shapeDisplay=obj.shape||'circle';const sizeDisplay=obj.size.toFixed(2);DOM.hoverCoord.innerHTML=`坐标<span>${coordStr}</span><br>形状<span>${shapeDisplay}</span>&nbsp;|&nbsp;尺寸<span>${sizeDisplay}</span>`;DOM.hoverPanel.style.display='block';hoveredPointIndex=found}else{DOM.hoverPanel.style.display='none';hoveredPointIndex=-1}}let panelFrameCount=0;let lastPanelFpsUpdate=performance.now();function updatePanelLoop(){panelFrameCount++;const now=performance.now();if(now-lastPanelFpsUpdate>=1000){DOM.fps.textContent=panelFrameCount;panelFrameCount=0;lastPanelFpsUpdate=now}if(performance.memory){const mem=performance.memory;const usedMB=(mem.usedJSHeapSize/1048576).toFixed(1);const limitMB=(mem.jsHeapSizeLimit/1048576).toFixed(1);DOM.memUsed.textContent=usedMB;DOM.memTotal.textContent=limitMB;const percent=(mem.usedJSHeapSize/mem.jsHeapSizeLimit*100);DOM.memPercent.textContent=percent.toFixed(1)+'%';if(lastMemSize){const diff=mem.usedJSHeapSize-lastMemSize;if(diff<0&&Math.abs(diff)>1024*1024){DOM.gcIndicator.textContent='🧹';DOM.gcIndicator.style.color='#ffaa44';setTimeout(()=>{DOM.gcIndicator.textContent='⚡';DOM.gcIndicator.style.color='#88ff88'},200)}}lastMemSize=mem.usedJSHeapSize}else{DOM.memUsed.textContent='N/A';DOM.memTotal.textContent='N/A';DOM.memPercent.textContent='--%'}const thetaDeg=(camera.theta*180/Math.PI);const phiDeg=(camera.phi*180/Math.PI);DOM.theta.textContent=thetaDeg.toFixed(1);DOM.phi.textContent=phiDeg.toFixed(1);DOM.dist.textContent=camera.distance.toFixed(1);DOM.tx.textContent=camera.target[0].toFixed(1);DOM.ty.textContent=camera.target[1].toFixed(1);DOM.tz.textContent=camera.target[2].toFixed(1);DOM.pointCount.textContent=testPoints.length;DOM.drawnCount.textContent=isPreviewMode?previewSorted.length:Math.min(drawIndex,sortedPoints.length);if(needsPick)performPick();requestAnimationFrame(updatePanelLoop)}let isDragging=false,prevMouseX=0,prevMouseY=0,dragButton=-1;canvas.addEventListener('contextmenu',(e)=>e.preventDefault());canvas.addEventListener('mousedown',(e)=>{if(e.button===0||e.button===2){isDragging=true;dragButton=e.button;prevMouseX=e.clientX;prevMouseY=e.clientY;needsReSort=true;scheduleRender()}});window.addEventListener('mouseup',()=>{isDragging=false});window.addEventListener('mousemove',(e)=>{mouseX=e.clientX;mouseY=e.clientY;needsPick=true;if(!isDragging)return;const dx=e.clientX-prevMouseX;const dy=e.clientY-prevMouseY;if(dragButton===0){camera.theta-=dx*RENDER_CONFIG.ROTATION_SPEED;camera.phi+=dy*RENDER_CONFIG.ROTATION_SPEED;camera.phi=Math.max(-Math.PI/2+0.01,Math.min(Math.PI/2-0.01,camera.phi))}else if(dragButton===2){const view=camera.tick();const scale=RENDER_CONFIG.PAN_SPEED*camera.distance;const moveX=-dx*scale;const moveY=dy*scale;const r=view.right,u=view.up;camera.target[0]+=r[0]*moveX+u[0]*moveY;camera.target[1]+=r[1]*moveX+u[1]*moveY;camera.target[2]+=r[2]*moveX+u[2]*moveY}prevMouseX=e.clientX;prevMouseY=e.clientY;needsReSort=true;scheduleRender()});canvas.addEventListener('wheel',(e)=>{e.preventDefault();const factor=e.deltaY>0?RENDER_CONFIG.ZOOM_SPEED:1/RENDER_CONFIG.ZOOM_SPEED;camera.distance=Math.max(RENDER_CONFIG.DISTANCE_MIN,Math.min(RENDER_CONFIG.DISTANCE_MAX,camera.distance*factor));needsReSort=true;scheduleRender()},{passive:false});canvas.addEventListener('mouseleave',()=>{DOM.hoverPanel.style.display='none';hoveredPointIndex=-1;needsPick=false});const keyState={};window.addEventListener('keydown',(e)=>{const key=e.key.toLowerCase();keyState[key]=true;if(key==='r'){const initCam=(config&&config.camera)?config.camera:{};camera.target=initCam.target?initCam.target.slice():[0,0,0];camera.distance=initCam.distance||25;camera.theta=initCam.theta||0.5;camera.phi=initCam.phi||0.4;needsReSort=true;scheduleRender();DOM.hoverPanel.style.display='none';hoveredPointIndex=-1}});window.addEventListener('keyup',(e)=>{keyState[e.key.toLowerCase()]=false});function handleKeyPan(){const speed=RENDER_CONFIG.KEY_PAN_SPEED*camera.distance;let dx=0,dy=0,dz=0;if(keyState['w'])dz+=speed;if(keyState['s'])dz-=speed;if(keyState['a'])dx-=speed;if(keyState['d'])dx+=speed;if(keyState['e'])dy-=speed;if(keyState['q'])dy+=speed;if(dx!==0||dy!==0||dz!==0){const view=camera.tick();const r=view.right,u=view.up,f=view.forward;const move=[r[0]*dx+u[0]*dy+f[0]*dz,r[1]*dx+u[1]*dy+f[1]*dz,r[2]*dx+u[2]*dy+f[2]*dz];camera.target[0]+=move[0];camera.target[1]+=move[1];camera.target[2]+=move[2];needsReSort=true;scheduleRender()}requestAnimationFrame(handleKeyPan)}function initScene(){const data=window.__EMBEDDED_DATA__;const rawConfig=data.config||{};config=deepMerge(DEFAULT_CONFIG,rawConfig);if(data.metadata&&data.metadata.background){config.background=data.metadata.background}sceneBackground=config.background;const camCfg=config.camera||{};camera.target=camCfg.target?camCfg.target.slice():[0,0,0];camera.distance=camCfg.distance||25;camera.theta=camCfg.theta||0.5;camera.phi=camCfg.phi||0.4;testPoints=data.testPoints||[];console.log('✅ 加载 '+testPoints.length+' 个点');renderTitle();renderLegend();forceFullRender=true;scheduleRender()}function renderTitle(){const titleEl=document.getElementById('title');if(config&&config.title){titleEl.textContent=config.title;titleEl.style.display='block'}else{titleEl.style.display='none'}}function renderLegend(){const container=document.getElementById('legend');const items=(config&&config.legend)?config.legend:[];if(!items.length){container.style.display='none';return}container.style.display='block';let html='<div class="legend-title">图例</div>';for(const item of items){const color=item.color||'#ffffff';const label=item.label||'';const[r,g,b]=parseColor(color);html+=`<div class="legend-item"><span class="legend-swatch"style="background:rgb(${r * 255 | 0},${g * 255 | 0},${b * 255 | 0});"></span><span class="legend-label">${label}</span></div>`}container.innerHTML=html}resizeCanvas();requestAnimationFrame(updatePanelLoop);handleKeyPan();needsReSort=true;initScene();console.log('3PR 查看器启动 (纯嵌入数据模式)');</script></body></html>"""

    def __init__(
        self,
        title: Optional[str] = None,
        background: Optional[str] = None,
        camera: Optional[Dict[str, Any]] = None,
        axis: Optional[Dict[str, Any]] = None,
        legend: Optional[List[Dict[str, str]]] = None,
    ):
        """
        创建一个场景。

        Args:
            title: 页面标题，显示在顶部。
            background: 背景色，CSS 颜色字符串。
            camera: 相机参数，如 {'distance': 25, 'theta': 0.5, 'phi': 0.4, 'target': [0,0,0]}。
            axis: 坐标轴配置，如 {'enabled': True, 'x': {'label':'X', 'color':'#ff5555'}, ...}。
            legend: 图例列表，如 [{'label':'类别A', 'color':'#ff8800'}, ...]。
        """
        # 初始化配置字典
        self.config: Dict[str, Any] = {}
        if title is not None:
            self.config['title'] = title
        if background is not None:
            self.config['background'] = background
        if camera is not None:
            self.config['camera'] = self._normalize_camera(camera)
        if axis is not None:
            self.config['axis'] = self._normalize_axis(axis)
        if legend is not None:
            self.config['legend'] = self._normalize_legend(legend)

        # 点列表
        self.points: List[Dict[str, Any]] = []

    # ---------- 内部工具 ----------
    @staticmethod
    def _normalize_color(color: Union[str, tuple, list]) -> str:
        """
        将多种颜色格式统一为 '#rrggbb' 紧凑字符串。
        支持：
            - '#ff0000' 或 '#f00'
            - (1.0, 0.0, 0.0) 或 (255, 0, 0)
            - [1.0, 0.0, 0.0] 或 [255, 0, 0]
        """
        if isinstance(color, str):
            c = color.strip()
            if c.startswith('#'):
                if len(c) == 4:  # #rgb
                    r = c[1]*2
                    g = c[2]*2
                    b = c[3]*2
                    return f'#{r}{g}{b}'
                elif len(c) == 7:  # #rrggbb
                    return c.lower()
                else:
                    raise ValueError(f"Invalid hex color: {color}")
            else:
                raise ValueError(f"Only hex colors supported, got: {color}")
        if isinstance(color, (list, tuple)):
            if len(color) != 3:
                raise ValueError("Color tuple/list must have length 3")
            # 判断是 0~1 还是 0~255
            if all(isinstance(v, numbers.Number) for v in color):
                vals = []
                for v in color:
                    if v > 1.0:
                        # 认为是 0~255
                        vals.append(int(round(v)))
                    else:
                        vals.append(int(round(v * 255)))
                # 钳制
                vals = [max(0, min(255, v)) for v in vals]
                return f'#{vals[0]:02x}{vals[1]:02x}{vals[2]:02x}'
            else:
                raise ValueError("Color values must be numbers")
        raise ValueError(f"Unsupported color format: {color}")

    @staticmethod
    def _normalize_camera(cam: Dict[str, Any]) -> Dict[str, Any]:
        """规范化相机参数，确保包含必要字段。"""
        allowed = {'distance', 'theta', 'phi', 'target'}
        result = {}
        for k, v in cam.items():
            if k not in allowed:
                continue
            if k == 'target':
                if not (isinstance(v, (list, tuple)) and len(v) == 3):
                    raise ValueError("target must be list/tuple of length 3")
                result[k] = list(v)
            else:
                if not isinstance(v, numbers.Number):
                    raise ValueError(f"{k} must be a number")
                result[k] = float(v)
        # 设置默认值（如果缺失）
        result.setdefault('distance', 25.0)
        result.setdefault('theta', 0.5)
        result.setdefault('phi', 0.4)
        result.setdefault('target', [0.0, 0.0, 0.0])
        return result

    @staticmethod
    def _normalize_axis(axis: Dict[str, Any]) -> Dict[str, Any]:
        """规范化坐标轴配置。"""
        result = {}
        # enabled
        if 'enabled' in axis:
            result['enabled'] = bool(axis['enabled'])
        else:
            result['enabled'] = True

        # 各轴标签和颜色
        for ax in ('x', 'y', 'z'):
            if ax in axis and isinstance(axis[ax], dict):
                sub = {}
                if 'label' in axis[ax]:
                    sub['label'] = str(axis[ax]['label'])
                if 'color' in axis[ax]:
                    sub['color'] = Scene._normalize_color(axis[ax]['color'])
                if sub:
                    result[ax] = sub

        # leftHanded
        if 'leftHanded' in axis:
            result['leftHanded'] = bool(axis['leftHanded'])
        # length
        if 'length' in axis:
            result['length'] = float(axis['length'])

        # 填充默认值
        result.setdefault('x', {'label': 'X', 'color': '#ff5555'})
        result.setdefault('y', {'label': 'Y', 'color': '#55ff55'})
        result.setdefault('z', {'label': 'Z', 'color': '#5588ff'})
        result.setdefault('leftHanded', False)
        result.setdefault('length', 500.0)
        return result

    @staticmethod
    def _normalize_legend(legend: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """规范化图例列表。"""
        result = []
        for item in legend:
            if not isinstance(item, dict):
                raise ValueError("Legend items must be dict")
            label = item.get('label', '')
            color = item.get('color', '#ffffff')
            result.append({
                'label': str(label),
                'color': Scene._normalize_color(color)
            })
        return result

    # ---------- 配置方法 ----------
    def set_title(self, title: str) -> None:
        """设置标题。"""
        self.config['title'] = str(title)

    def set_background(self, color: str) -> None:
        """设置背景色。"""
        self.config['background'] = self._normalize_color(color)

    def set_camera(
        self,
        distance: float = 25.0,
        theta: float = 0.5,
        phi: float = 0.4,
        target: Union[List[float], tuple] = (0.0, 0.0, 0.0)
    ) -> None:
        """设置相机参数。"""
        self.config['camera'] = {
            'distance': float(distance),
            'theta': float(theta),
            'phi': float(phi),
            'target': list(target)
        }

    def set_axis(
        self,
        enabled: bool = True,
        x_label: str = "X",
        y_label: str = "Y",
        z_label: str = "Z",
        x_color: str = "#ff5555",
        y_color: str = "#55ff55",
        z_color: str = "#5588ff",
        left_handed: bool = False,
        length: float = 500.0
    ) -> None:
        """配置坐标轴。"""
        self.config['axis'] = {
            'enabled': enabled,
            'x': {'label': x_label, 'color': self._normalize_color(x_color)},
            'y': {'label': y_label, 'color': self._normalize_color(y_color)},
            'z': {'label': z_label, 'color': self._normalize_color(z_color)},
            'leftHanded': left_handed,
            'length': float(length)
        }

    def add_legend(self, label: str, color: str) -> None:
        """添加一个图例项。"""
        if 'legend' not in self.config:
            self.config['legend'] = []
        self.config['legend'].append({
            'label': str(label),
            'color': self._normalize_color(color)
        })

    def set_legend(self, legend: List[Dict[str, str]]) -> None:
        """直接设置图例列表（覆盖）。"""
        self.config['legend'] = self._normalize_legend(legend)

    def update_layout(self, **kwargs) -> None:
        """
        灵活更新配置，支持以下键：
            title, background, camera, axis, legend
        其中 camera, axis, legend 会进行合并（而不是完全覆盖）。
        """
        for key, value in kwargs.items():
            if key == 'camera':
                cur = self.config.get('camera', {})
                cur.update(self._normalize_camera(value))
                self.config['camera'] = cur
            elif key == 'axis':
                cur = self.config.get('axis', {})
                cur.update(self._normalize_axis(value))
                self.config['axis'] = cur
            elif key == 'legend':
                self.config['legend'] = self._normalize_legend(value)
            elif key in ('title', 'background'):
                self.config[key] = value
            else:
                # 其他键直接设置（允许扩展）
                self.config[key] = value

    # ---------- 点操作 ----------
    def add_point(
        self,
        pos: Union[List[float], tuple],
        color: Optional[Union[str, tuple, list]] = None,
        size: float = 1.0,
        shape: str = 'circle',
        meta: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        添加一个点。

        Args:
            pos: [x, y, z] 坐标。
            color: 颜色，支持 hex 字符串或 RGB 元组/列表。
            size: 大小（像素）。
            shape: 形状，可选 'circle', 'square', 'triangle', 'diamond', 'star', 'cross'。
            meta: 附加元数据字典。
        """
        if not (isinstance(pos, (list, tuple)) and len(pos) == 3):
            raise ValueError("pos must be list/tuple of length 3")
        if not isinstance(size, numbers.Number):
            raise ValueError("size must be a number")
        valid_shapes = {'circle', 'square', 'triangle', 'diamond', 'star', 'cross'}
        if shape not in valid_shapes:
            raise ValueError(f"Unsupported shape: {shape}")
        if meta is not None and not isinstance(meta, dict):
            raise ValueError("meta must be dict or None")

        point = {
            'pos': [float(p) for p in pos],
            'size': float(size)
        }
        if color is not None:
            point['color'] = self._normalize_color(color)
        else:
            point['color'] = '#ffffff'  # 默认白色
        if shape != 'circle':
            point['shape'] = shape
        if meta:
            point['meta'] = meta

        self.points.append(point)

    def add_points(self, points_data: Iterable[Union[Dict, tuple, list]]) -> None:
        """
        批量添加点。支持两种格式：

        1. 字典：必须包含 'pos'，可选 'color', 'size', 'shape', 'meta'。
        2. 元组/列表：顺序为 (pos, color, size, shape, meta)，后四项可选。
        """
        for item in points_data:
            if isinstance(item, dict):
                pos = item.get('pos')
                if pos is None:
                    raise ValueError("Dict point must contain 'pos'")
                color = item.get('color')
                size = item.get('size', 1.0)
                shape = item.get('shape', 'circle')
                meta = item.get('meta')
                self.add_point(pos, color, size, shape, meta)
            elif isinstance(item, (list, tuple)):
                if len(item) < 1:
                    raise ValueError("Each point tuple must have at least pos")
                pos = item[0]
                color = item[1] if len(item) > 1 else None
                size = item[2] if len(item) > 2 else 1.0
                shape = item[3] if len(item) > 3 else 'circle'
                meta = item[4] if len(item) > 4 else None
                self.add_point(pos, color, size, shape, meta)
            else:
                raise ValueError("Each point must be dict or tuple/list")

    # ---------- 导出 ----------
    def to_dict(self) -> Dict[str, Any]:
        """生成符合查看器规范的完整数据结构。"""
        result = {}
        # 只添加非空的 config
        if self.config:
            result['config'] = self.config
        if self.points:
            result['testPoints'] = self.points
        return result

    def to_json(self, compact: bool = True, **kwargs) -> str:
        """
        输出 JSON 字符串。

        Args:
            compact: 是否压缩（无多余空格），默认 True。
            **kwargs: 传递给 json.dumps 的参数。
        """
        data = self.to_dict()
        if compact:
            kwargs.setdefault('separators', (',', ':'))
            kwargs.setdefault('ensure_ascii', False)
        else:
            kwargs.setdefault('indent', 2)
        return json.dumps(data, **kwargs)

    def save_json(self, filename: str, compact: bool = True, **kwargs) -> None:
        """保存 JSON 到文件。"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, **kwargs)

    def write_html(self, filename: str, open_browser: bool = False) -> None:
        """
        生成独立的 HTML 文件，内嵌点云数据和配置。

        Args:
            filename: 输出文件名。
            open_browser: 是否自动打开。
        """
        if not self._HTML_TEMPLATE:
            raise ValueError(
                "Scene._HTML_TEMPLATE is empty. Please assign the full compressed HTML content "
                "to Scene._HTML_TEMPLATE, and ensure it contains the placeholder '__DATA_PLACEHOLDER__'."
            )

        data_json = self.to_json(compact=True)
        html_content = self._HTML_TEMPLATE.replace('__DATA_PLACEHOLDER__', data_json)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        if open_browser:
            webbrowser.open('file://' + os.path.abspath(filename))

    def show(self) -> None:
        """生成临时 HTML 文件并在默认浏览器中打开（类似 plotly 的 show()）。"""
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            tmp_path = tmp.name
        self.write_html(tmp_path, open_browser=True)
        print(f"临时文件已生成: {tmp_path}")

# =============================================================================
# 辅助函数（可选）
# =============================================================================
def set_html_template(template: str) -> None:
    """设置 Scene 类的 HTML 模板（全局）。"""
    Scene._HTML_TEMPLATE = template