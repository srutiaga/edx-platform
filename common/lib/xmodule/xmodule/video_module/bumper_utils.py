"""
Utils for video bumper
"""
import json


from django.conf import settings

try:
    import edxval.api as edxval_api
except ImportError:
    edxval_api = None


def is_bumper_enabled(video):
    """
    Check if bumper enabled
    """
    return bool(
        settings.FEATURES.get('ENABLE_VIDEO_BUMPER') and
        getattr(video, 'video_bumper') and
        edxval_api
    )


def bumperize(video):
    """
    Populate video with bumper settings, if they presented

    Return tuple:
        bumper_enabled (bool), bumper_metadata (dict)
    """
    video.bumper = {
        'enabled': is_bumper_enabled(video),
        'edx_video_id': "",
        'transcripts': {},
        'metadata': {}
    }

    if not video.bumper['enabled']:
        return

    bumper_settings = getattr(video, 'video_bumper', None)
    try:
        edx_video_id, transcripts = bumper_settings['video'], bumper_settings['transcripts']
    except TypeError, KeyError:
        video.bumper['enabled'] = False
        return

    video.bumper.update({
        'enabled': True,
        'edx_video_id': edx_video_id,
        'transcripts': transcripts,
    })

    sources = get_sources(video)
    if not sources:
        video.bumper['enabled'] = False
        return

    video.bumper.update({
        'metadata': metadata(video, sources)
    })


def get_sources(video):
    """
    Get bumper sources from edxval.

    Returns list of sources.
    """
    try:
        val_profiles = ["desktop_webm", "desktop_mp4"]
        val_video_urls = edxval_api.get_urls_for_profiles(video.bumper['edx_video_id'], val_profiles)
        bumper_sources = filter(None, [val_video_urls[p] for p in val_profiles])
    except edxval_api.ValInternalError:
        # if no bumper sources, nothing will be showed
        log.warning("Could not retrieve information from VAL for Bumper edx Video ID: %s.", video.bumper['edx_video_id'])
        return []

    return bumper_sources


def metadata(video, sources):
    """
    Generate bumper metadata.
    """
    unused_track_url, bumper_transcript_language, bumper_languages = video.get_transcripts_for_student(video.bumper['transcripts'], bumper=True)

    bumper_metadata = {
        # Why we dumps sources in video but not here?
        'sources': sources,
        'showCaptions': json.dumps(bool(video.bumper['transcripts'])),  # Send it, Anton?
        'transcriptLanguage': bumper_transcript_language,
        'transcriptLanguages': bumper_languages if video.bumper['transcripts'] else {},
        'transcriptTranslationUrl': video.runtime.handler_url(video, 'transcript', 'translation_bumper').rstrip('/?'),
        'transcriptAvailableTranslationsUrl': video.runtime.handler_url(video, 'transcript', 'available_translations_bumper').rstrip('/?'),
    }

    return bumper_metadata
