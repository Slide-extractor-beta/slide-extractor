# slide-extractor
An easy tool to extract slides from presentations ( lectures 😉 )

<h3>Usage</h3>

`slide-extractor -p <path> -s <number> -d <number>`

<h5>Flags</h5>

- `-p or --path` : Provides the path for the video file <b>( * required)</b>
- `-s or --skip` : Provides the skip seconds for the video.( Captures the video's frames at interval of specified value )
- `-d or --diff` : Specifies the difference level between current and previous slide ( a slide is included iff the difference is higher than the specified value)
- `-h or --help` : Help Menu

Try adjusting the `diff` value if you think all slides aren't being captured or too many slides are being captured.

Too Low `diff` value will make the extractor captures slides even with slight difference.

Too  High `diff` value might make the extractor skip certain slides.
