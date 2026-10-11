// Yalnızca TEST için: raylib 5.x API'sinin Ekin'in kullandığı kısmının bildirimleri.
// Gerçek raylib kurulu olmadan grafik çıktısının sözdizimini denetlemeye yarar
// (g++ -fsyntax-only). Gerçek programlar için https://www.raylib.com kullanın.
#pragma once
#include <stdbool.h>

typedef struct Vector2 { float x; float y; } Vector2;
typedef struct Vector3 { float x; float y; float z; } Vector3;
typedef struct Color { unsigned char r; unsigned char g; unsigned char b; unsigned char a; } Color;
typedef struct Rectangle { float x; float y; float width; float height; } Rectangle;
typedef struct Texture { unsigned int id; int width; int height; int mipmaps; int format; } Texture;
typedef Texture Texture2D;
typedef struct RenderTexture { unsigned int id; Texture texture; Texture depth; } RenderTexture;
typedef RenderTexture RenderTexture2D;
typedef struct GlyphInfo { int value; int offsetX; int offsetY; int advanceX; } GlyphInfo;
typedef struct Font { int baseSize; int glyphCount; int glyphPadding; Texture2D texture; Rectangle *recs; GlyphInfo *glyphs; } Font;
typedef struct Camera3D { Vector3 position; Vector3 target; Vector3 up; float fovy; int projection; } Camera3D;
typedef struct Image { void *data; int width; int height; int mipmaps; int format; } Image;

#define CLITERAL(type) type
#define WHITE CLITERAL(Color){ 255, 255, 255, 255 }
#define BLACK CLITERAL(Color){ 0, 0, 0, 255 }

typedef enum { FLAG_VSYNC_HINT = 0x00000040, FLAG_MSAA_4X_HINT = 0x00000020 } ConfigFlags;
typedef enum { LOG_ALL = 0, LOG_TRACE, LOG_DEBUG, LOG_INFO, LOG_WARNING, LOG_ERROR } TraceLogLevel;
typedef enum { TEXTURE_FILTER_POINT = 0, TEXTURE_FILTER_BILINEAR } TextureFilter;
typedef enum { MOUSE_BUTTON_LEFT = 0, MOUSE_BUTTON_RIGHT = 1 } MouseButton;
typedef enum { CAMERA_PERSPECTIVE = 0, CAMERA_ORTHOGRAPHIC } CameraProjection;

#ifdef __cplusplus
extern "C" {
#endif
void InitWindow(int width, int height, const char *title);
bool WindowShouldClose(void);
void CloseWindow(void);
void SetConfigFlags(unsigned int flags);
void SetTraceLogLevel(int logLevel);
void SetExitKey(int key);
void SetTargetFPS(int fps);
float GetFrameTime(void);
void ClearBackground(Color color);
void BeginDrawing(void);
void EndDrawing(void);
void BeginMode3D(Camera3D camera);
void EndMode3D(void);
void BeginTextureMode(RenderTexture2D target);
void EndTextureMode(void);
RenderTexture2D LoadRenderTexture(int width, int height);
void UnloadRenderTexture(RenderTexture2D target);
bool FileExists(const char *fileName);
Font LoadFontEx(const char *fileName, int fontSize, int *codepoints, int codepointCount);
void UnloadFont(Font font);
void SetTextureFilter(Texture2D texture, int filter);
void DrawCircleV(Vector2 center, float radius, Color color);
void DrawRing(Vector2 center, float innerRadius, float outerRadius, float startAngle, float endAngle, int segments, Color color);
void DrawEllipse(int centerX, int centerY, float radiusH, float radiusV, Color color);
void DrawRectangleRec(Rectangle rec, Color color);
void DrawRectangleLinesEx(Rectangle rec, float lineThick, Color color);
void DrawLineEx(Vector2 startPos, Vector2 endPos, float thick, Color color);
void DrawTriangle(Vector2 v1, Vector2 v2, Vector2 v3, Color color);
void DrawPixelV(Vector2 position, Color color);
void DrawTextEx(Font font, const char *text, Vector2 position, float fontSize, float spacing, Color tint);
void DrawText(const char *text, int posX, int posY, int fontSize, Color color);
Vector2 MeasureTextEx(Font font, const char *text, float fontSize, float spacing);
int MeasureText(const char *text, int fontSize);
int GetMouseX(void);
int GetMouseY(void);
bool IsMouseButtonDown(int button);
bool IsMouseButtonPressed(int button);
bool IsKeyDown(int key);
bool IsKeyPressed(int key);
void DrawTextureRec(Texture2D texture, Rectangle source, Vector2 position, Color tint);
void DrawCubeWires(Vector3 position, float width, float height, float length, Color color);
void DrawLine3D(Vector3 startPos, Vector3 endPos, Color color);
Image LoadImageFromTexture(Texture2D texture);
void ImageFlipVertical(Image *image);
bool ExportImage(Image image, const char *fileName);
void UnloadImage(Image image);
#ifdef __cplusplus
}
#endif
