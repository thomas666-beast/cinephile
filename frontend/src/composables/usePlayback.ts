import { ref } from "vue";
import { playbackApi } from "../api";
import type { PlaybackResponse } from "../api/types";

export type PlaybackState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "ready"; data: PlaybackResponse }
  | { kind: "processing" }     // 409 from backend
  | { kind: "unsubscribed" }   // 403
  | { kind: "notfound" }       // 404
  | { kind: "error"; message?: string };

export function usePlayback() {
  const state = ref<PlaybackState>({ kind: "idle" });

  async function fetchPlayback(kind: "movie", slug: string): Promise<void>;
  async function fetchPlayback(kind: "episode", id: number): Promise<void>;
  async function fetchPlayback(kind: "movie" | "episode", ident: string | number) {
    state.value = { kind: "loading" };
    try {
      const data = kind === "movie"
        ? await playbackApi.movie(ident as string)
        : await playbackApi.episode(ident as number);
      if (!data.hls_manifest_url) {
        // Playback API returns 200 with null manifest for non-ready assets
        // (in this design we return 409, but defensive)
        state.value = { kind: "processing" };
      } else {
        state.value = { kind: "ready", data };
      }
    } catch (e: any) {
      const status = e?.response?.status;
      if (status === 401) {
        state.value = { kind: "unsubscribed" };
      } else if (status === 403) {
        state.value = { kind: "unsubscribed" };
      } else if (status === 404) {
        state.value = { kind: "notfound" };
      } else if (status === 409) {
        state.value = { kind: "processing" };
      } else {
        state.value = { kind: "error", message: e?.message };
      }
    }
  }

  return { state, fetchPlayback };
}
