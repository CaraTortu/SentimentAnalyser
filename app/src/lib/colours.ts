function hexToRgb(hex: string): { r: number; g: number; b: number } {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)!;
    return {
        r: parseInt(result[1]!, 16),
        g: parseInt(result[2]!, 16),
        b: parseInt(result[3]!, 16),
    };
}

function rgbToHex(r: number, g: number, b: number): string {
    return `#${[r, g, b]
        .map((x) =>
            Math.max(0, Math.min(255, Math.round(x)))
                .toString(16)
                .padStart(2, "0"),
        )
        .join("")}`;
}

function interpolateColor(color1: string, color2: string, t: number): string {
    const c1 = hexToRgb(color1);
    const c2 = hexToRgb(color2);
    return rgbToHex(
        c1.r + (c2.r - c1.r) * t,
        c1.g + (c2.g - c1.g) * t,
        c1.b + (c2.b - c1.b) * t,
    );
}

const CUTOFF_VAL = 0.3;

export function interpolateTriColour(value: number): string {
    const clamped = Math.max(0, Math.min(1, value));

    if (clamped <= CUTOFF_VAL) {
        // Interpolate from red to yellow between 0 and CUTOFF_VAL
        return interpolateColor("#fb2c36", "#f0b100", clamped / CUTOFF_VAL);
    } else {
        // Interpolate from yellow to green between CUTOFF_VAL and 1
        return interpolateColor(
            "#f0b100",
            "#05df72",
            (clamped - CUTOFF_VAL) / (1 - CUTOFF_VAL),
        );
    }
}
