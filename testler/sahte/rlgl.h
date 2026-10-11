// Yalnızca TEST için: raylib rlgl.h API'sinin Ekin'in kullandığı kısmı.
#pragma once
#define RL_LINES 0x0001
#define RL_TRIANGLES 0x0004
#define RL_QUADS 0x0007

#ifdef __cplusplus
extern "C" {
#endif
void rlPushMatrix(void);
void rlPopMatrix(void);
void rlTranslatef(float x, float y, float z);
void rlRotatef(float angle, float x, float y, float z);
void rlScalef(float x, float y, float z);
void rlBegin(int mode);
void rlEnd(void);
void rlVertex3f(float x, float y, float z);
void rlColor4ub(unsigned char r, unsigned char g, unsigned char b, unsigned char a);
void rlEnableBackfaceCulling(void);
void rlDrawRenderBatchActive(void);
void rlDisableBackfaceCulling(void);
#ifdef __cplusplus
}
#endif
