function minutesToKoreanDuration(minutes: number): string {
    const hrs = Math.floor(minutes / 60);
    const mins = minutes % 60;
    let result = "";
    if (hrs > 0) {
        result += `${hrs}시간 `;
    }
    if (mins > 0) {
        result += `${mins}분`;
    }
    return result.trim();
}

export { minutesToKoreanDuration };
