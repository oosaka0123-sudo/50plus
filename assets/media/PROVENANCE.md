# Media Provenance — Issue #58 Claude-first media redesign

Generated: 2026-09-09
Provider: Google
Image model: `gemini-2.5-flash-image`
Video model: `veo-3.1-fast-generate-001`

This file documents where each committed media asset came from. No secrets,
tokens, or credentials are recorded here or anywhere else in this mapping.

## Source verification

The 10 source gs:// URIs below were verified during the Issue #58 Google Media MCP generation session before implementation. No secret values are included.

## Images (8 total)

Source: 8 PNGs generated via Google Media MCP `generate_image`
(`gemini-2.5-flash-image`), staged locally outside the repository at
`50plus-media-staging/images/`, then converted to WebP and committed under
`assets/media/images/`. Original PNGs are not committed.

| Staged filename | Final asset(s) | GCS source URI | Prompt intent |
| --- | --- | --- | --- |
| `image_20260909-024720_2ff5d6f4.png` | `hero-community-plaza-640.webp`, `hero-community-plaza-1280.webp` | `gs://rss7-ai-media-genmedia/projects/50plus/images/2026/09/image_20260909-024720_2ff5d6f4.png` | Golden-hour city plaza, five adults 50+ in smart-casual clothing laughing together mid-conversation; home hero poster / video fallback still. |
| `image_20260909-024726_c24a0890.png` | `street-walk-dusk-640.webp`, `street-walk-dusk-1280.webp` | `gs://rss7-ai-media-genmedia/projects/50plus/images/2026/09/image_20260909-024726_c24a0890.png` | Four adults 50+ walking and talking together down a quiet shopping street at dusk; used for the 街歩き・散策 (walking) theme. |
| `image_20260909-024734_9ba563b9.png` | `pottery-studio-640.webp`, `pottery-studio-1280.webp` | `gs://rss7-ai-media-genmedia/projects/50plus/images/2026/09/image_20260909-024734_9ba563b9.png` | Four adults 50+ at a bright pottery studio, working clay on wheels together and laughing; used for the 文化・ものづくり (culture/craft) theme. |
| `image_20260909-024741_f913e023.png` | `garden-autumn-walk-640.webp`, `garden-autumn-walk-1280.webp` | `gs://rss7-ai-media-genmedia/projects/50plus/images/2026/09/image_20260909-024741_f913e023.png` | Six adults 50+ walking a wooden boardwalk through a Japanese garden in autumn color; used for the アウトドア (outdoor) theme and as a generic editorial image on the listings page. |
| `image_20260909-024748_0b47b21b.png` | `park-stretch-sakura-640.webp`, `park-stretch-sakura-1280.webp` | `gs://rss7-ai-media-genmedia/projects/50plus/images/2026/09/image_20260909-024748_0b47b21b.png` | Five adults 50+ doing light group stretching in a park under cherry blossoms; used for the スポーツ (sports) theme and as the activities-page video poster. |
| `image_20260909-024756_f988e0ed.png` | `izakaya-evening-640.webp`, `izakaya-evening-1280.webp` | `gs://rss7-ai-media-genmedia/projects/50plus/images/2026/09/image_20260909-024756_f988e0ed.png` | Four adults 50+ sharing food and drinks at an izakaya table, mid-laugh; used for the 食・交流 (food/social) theme. |
| `image_20260909-024802_edeb109c.png` | `garden-volunteer-640.webp`, `garden-volunteer-1280.webp` | `gs://rss7-ai-media-genmedia/projects/50plus/images/2026/09/image_20260909-024802_edeb109c.png` | Four adults 50+ in sun hats and gloves doing community flower-bed and litter cleanup; used for the ボランティア (volunteer) theme and reused on the contact page. |
| `image_20260909-024809_8f92e32f.png` | `plaza-conversation-calm-640.webp`, `plaza-conversation-calm-1280.webp` | `gs://rss7-ai-media-genmedia/projects/50plus/images/2026/09/image_20260909-024809_8f92e32f.png` | Four adults 50+ standing and talking calmly in an open plaza at golden hour; used as the About-page mission image. |

Conversion: Pillow (`PIL.Image`), resized to 640px- and 1280px-wide variants
(source PNGs were 1344×768), saved as WebP at quality 74, method 6. No crop or
retouching was applied beyond resizing and format conversion.

## Videos (2 total)

Source: 2 MP4s generated via Google Media MCP `generate_video`
(`veo-3.1-fast-generate-001`), staged locally outside the repository at
`50plus-media-staging/videos/`, then copied byte-for-byte into
`assets/media/video/`. No transcoding was performed (ffmpeg is not available
in this environment).

| Staged filename | Final asset | GCS source URI | Prompt intent |
| --- | --- | --- | --- |
| `video_20260909-024935_bd84489e.mp4` | `hero-loop.mp4` | `gs://rss7-ai-media-genmedia/projects/50plus/videos/2026/09/video_20260909-024935_bd84489e.mp4` | Cinematic, gently moving lifestyle loop for the home hero background; muted/looped/autoplay-safe. |
| `video_20260909-024937_9787ab70.mp4` | `activities-loop.mp4` | `gs://rss7-ai-media-genmedia/projects/50plus/videos/2026/09/video_20260909-024937_9787ab70.mp4` | Restrained secondary loop for the activities page, played only on user request (`preload="none"`, no autoplay). |

Video-to-page assignment (hero vs. activities) was made by generation order,
matching the intended hero-first / secondary-second sequence from the Issue
#58 brief. This environment has no video decoder available (no ffmpeg,
`opencv-python`, `av`, or `moviepy`), so the actual frame content of each file
could not be visually inspected before assignment. If either loop turns out
to suit the other placement better, swapping the two `src`/`poster`
references in `index.html` and `activities.html` is a no-risk fix.

## No fabricated facts

None of the images or videos listed above depict, or are captioned as
depicting, any specific real venue, organizer, participant, or event from
`data/verified-listings.json`. Every page that uses this media includes a
visible caption stating the media is illustrative (「写真はイメージです」/
「映像はイメージです」) and does not represent real people, groups, or
occurrences.

## Derived social preview

`assets/media/social/og-50plus.jpg` is not a new AI generation. It is derived
from the committed `hero-community-plaza-1280.webp` still for social link
previews. The image was center-cropped and resized to 1200×630, then saved as
a progressive JPEG at quality 85. No retouching, new factual claims, or
additional remote media generation were involved.

The file is referenced by Open Graph and Twitter/X card metadata on the
indexable public pages.
