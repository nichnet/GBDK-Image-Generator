import example_data
import gbdkimg

if __name__ == "__main__":
    quads = gbdkimg.generateQuadrants(example_data.t32_32)
    ordered = gbdkimg.sortQuadrants(quads)
    gbdkimg.exportImage(ordered, "export")
