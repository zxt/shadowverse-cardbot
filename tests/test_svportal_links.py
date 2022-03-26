import decklist


def test_svportal_link_hash_valid():
    link = ["3.1.76QHo.7AJJS.7AJJS.7AJJS.7Hv9C.7Hv9C.7Hv9C.7Hvtw.7Hvtw." +
            "7Hvtw.7Lhag.7Hsj6.7Hsj6.7Hsj6.7LlkI.7LlkI.7LlkI.7AEw2.7AEw2." +
            "7AEw2.7AB_0.7AB_0.7AB_0.7AJJI.7AJJI.7AJJI.7E7SS.7E7SS.7E7SS." +
            "7AJJc.7AJJc.7AJJc.76Sk2.76Sk2.76Sk2.76Ns0.76Ns0.76Ns0." +
            "7E50C.76VAc"]

    output = decklist.process_svportal_links(link)
    assert "Forestcraft" in output
    assert "Constructed (Unlimited)" in output
    assert "View this deck in SV-Portal" in output
    assert "/deck/" in output


def test_svportal_crosscraft_link_hash_valid():
    link = ["6.6.7.78Hw2.78Hw2.78Hw2.7JkqI.7JkqI.7JkqI.7LNJy.7LNJy.7C8VI." +
            "7C8VI.7C8VI.7JpyQ.7JpyQ.7JpyQ.7G1X6.7G1X6.7G1X6.7Jrfy.7Jrfy." +
            "7Jrfy.7CVCQ.7CVCQ.7CVCQ.7O2DS.7O2DS.7O2DS.7O2Dc.7O2Dc.7JmnI." +
            "7JmnI.7JmnI.78lDC.78lDC.78lDC.7G1Wy.7G1Wy.7G1Wy.7JmnS." +
            "7JmnS.7JmnS"]

    output = decklist.process_svportal_links(link)
    assert "Bloodcraft/Havencraft" in output
    assert "Cross Craft" in output
    assert "View this deck in SV-Portal" in output
    assert "/deck_co/" in output
