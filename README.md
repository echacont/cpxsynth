cpxsynth: Single operator FM synthesis for the Circuit Playground Express

v0.1: initial version supports midi noteOn/Off and CC14 (modulation ratio) and CC15 (modulation index). Bugs: Memory allocation errors occur when lower notes that G1 are played. Also, continuous control change patterns need handling before commiting to audio generation/reproduction.
