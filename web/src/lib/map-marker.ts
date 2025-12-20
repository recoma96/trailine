import { INTERVAL_DIFFICULTY_COLORS } from "@/vars/colors";

export function createMarkerHtml(index: number, difficultyLevel: number): string {
    const backgroundColor = INTERVAL_DIFFICULTY_COLORS[difficultyLevel];
    const markerStyle = [
        'w-[24px]',
        'h-[24px]',
        'text-white',
        'text-sm',
        'rounded-full',
        'flex',
        'items-center',
        'justify-center',
        'font-bold',
        'border-2',
    ].join(' ');

    return `<div class="${markerStyle}" style="background-color: ${backgroundColor}">${index}</div>`;
}
