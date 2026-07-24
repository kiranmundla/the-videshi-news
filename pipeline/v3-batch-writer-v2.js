export const meta = { name: "v3-batch-writer-v2", description: "Write V3 articles for The Videshi", phases: ["write-articles", "post-processing"] };

const ENV = "set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.pexels 2>/dev/null; set +a";

const candidates = [
  {
    "topic_id": "aa30fbf3-faf4-48cb-98d6-286ad07625e6",
    "title": "Sooryavanshi, Mayank help India end T20I losing streak - Cricinfo",
    "category": "sports",
    "coverage": "update",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMimAFBVV95cUxOaG8zd0lXQWpqMVV3eDdnSXpvcFdJUTNIc3k4Rmt2UmQ2VFVZRHFUaEw0Z3pfQ2R3d1NKV1Yzak02cGtUNm9sR0ZPVm5CQWRmbklVQlYyVXZsSFBXb0VJTzFuSHVsSkN2azVxbEp0UXVJLTVEM2tNa21GRDVaMXNGenNxNklyWHBGMEZENXRKTEhMNHRLanJrUQ?oc=5"
    ]
  },
  {
    "topic_id": "bb3f4d1d-2eda-478a-bca4-c334cda1b133",
    "title": "Indian Markets Crash: Sensex Down 900 Points as Brent Oil Tops $100",
    "category": "markets-finance",
    "coverage": "update",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMi9AFBVV95cUxQOXFoUEt4S2pHd2hpY0thLVd0WTV5ZThjSVdoel92bzNYSWZNZ1FpbVNhZkFrX184VEt1LWJsZjFFZ2ozemJfTFR5UDZqYzZzRUg4bnR5MzdMVWg5b2Y2UXVWNm1KcVVWVUN6RWt4cXR6LTJXU3M2eHNKdXhMdXFRNWNlZk9aUUhoUk1oNmh1RWdOU3ZZR3FRaGxJV0ZuVFZFS3RYQzh4RjJmR1A0R3BKRFpuR1ZqQXQxemxZVVk3WlRFQlVYRTdvMFVBUzBIWENnTmI1SEdjY3hQM2M3MnRFN1gzSXhPQjNCOHhTRVo5aWVxbFAw0gH6AUFVX3lxTE5YWm5ISnpxUWw4SlJkcWh2Y3ZibmZEZGZveHVDNDBxZWtlTnA3NWFaRUp6cW4xblFVWUl4eVVUeEV5Q3FyQzI2dEtldjlBcnJsZVk2SHdTTzNnRE5vb0YzQWpFU29SSVJyLUtUVDNaa3VPSGdCdHhJeXRjQjZ4X1Q0MnhVRUNmQ0RCSkFKX29Hc2JuZk9NMzR6YU1ualVGNUlpbUUtS2l0ZXlfcjlNN0hpRHF1MXB5RE11U1p6ZHV1MzhEcGZndWVPMWZ0eXNTQTduOFRoQ3RJN0FKeWJRLXFxTzNibTFLVG01MG1nV3hfS212ZjkyMXdkQmc?oc=5",
      "https://news.google.com/rss/articles/CBMikAFBVV95cUxPRFQ5dlQ0MFctUmdHMU5BcXNFUTVGN3hnb0owdVpYVW9xSmJra1BYbzRaLUZmLU5wX3BQR2lvVjA1N0o2ZkZrTkJjN3pTeThRUmZETmd5RFdDYnJubjFZT0N5LURVbWJxZ2s5Q2VpSHpwejUtajZJdDZRczlhanhxM3dwbnNxcGphRkJvNVJra2k?oc=5",
      "https://news.google.com/rss/articles/CBMizAFBVV95cUxPdmZ4SlY4VWczRU11Ni1TZjY1d1E2UEo3LVpHb2tOc3NFd0lDT05yTnpobXBhaXFxR3N2WVRrV1I3WHdKVGxYdW5lNUlyVXpQUUJVOVFDVnRsblZCcUd4RjFvTFNkQmhrbXZ4VjY0NVZYaFFnQkhOc21pTk00cjQ5UjZLRlBuVXFEY2pBN3VvMUVMNW5hdS0zaXB5OFJzYnBIRk5xSGU3aGk2T0dVRV83TUZzaVRmWHR4NkhQY2pnWkkxbHc2ZjZNUE9QeULSAdQBQVVfeXFMTzVrUVFyRUFuTU4wc2gwV3ZGX1lxeUF3RG1YbWVKZVB5NURsNGc5dkpybFFOQlhJWVczMGtKSENXWDQtZmNSWEhLWVU4N1ZKUHpweFpxWG9XZzNsRkhQNWhaT1R4RG00d0FFbldSdmVTeDdoYXU4RWR0cEhYMFNHY2ZKNmN4b3o4dE5QVTFRdC1FS3IwSlBiRjh3cWlwOEl2UDZ6MmlyRU0taUpHTFMyX0RZYVBaYzlBY05qOGFGU2d2Z2JVLVNFRVpnWldUVEoySGFhXzA?oc=5"
    ],
    "merge_topic_ids": [
      "bb3f4d1d-2eda-478a-bca4-c334cda1b133",
      "e6350162-12b1-4a43-b128-4178dbed2694"
    ]
  },
  {
    "topic_id": "23244c04-1b4d-461f-a44e-243ac4fcb680",
    "title": "Indian Migrant Worker Found Dead At Jerusalem Flat, Israeli Man Arrested - NDTV",
    "category": "news",
    "coverage": "update",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMiiAFBVV95cUxPTDY5TXNqQ2I0U1VNZGJlWVhCT29CRVB4M2ZoVUZ6SWgweVpSeU5fWnVNSTg4WnlzaC0xemVXYzR3YVM2QUZ1OFI4bGwwUDZKZjZZbzU2OW44TFR0YS1GMm14ay1HRDhnbWwxR0Y2V29Vd0IxblU0bzJscVBNNEZ0UzZFOHZmcERz0gGOAUFVX3lxTFBCWkphcllLWnU1X2NUUjJLSXBpNXc1QjRTNWNUVVhuTkVVWTJkbzVybkpOMVRpWHRrRlo5NEZLQTBHMElWOWdHMWdTS3EwV1E2QjQxQzFhWXZXbGFzWGVWWWNudWhlS2pxVHhQNnJ0a3c0eHh5NVRLQ3BMY0ZOb3RlWFljVldpYlUwSEJQWEE?oc=5",
      "https://news.google.com/rss/articles/CBMixAFBVV95cUxNR2dqWGpxTWVfQTVJT1ZjZjVoWDlmMUdnUFdFRjJmeXZuMkFVTFM5aEpkUEIwT1AyX25LODFncWwtWEIzWG9HaDlVN1k3WjRWUDhvOVk0U1BUYTNha29zNXFjMnhjcVZYeV9OMWptM1plYUFtOF9uTDM3eUFSWW54VW9ReWs0OEhIaEdHNUtsQmN1amljbzFqRVp2bTNqXzU3dDYyQl9TTVhhNml6YWx2dU9CVmo0TmpWUFF0bm1EU1dSWVE0?oc=5"
    ]
  },
  {
    "topic_id": "b10c03b2-45c6-41f4-a49c-16df7ede64e6",
    "title": "US government announces new global visa restriction policy; says: United States ",
    "category": "immigration",
    "coverage": "update",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMikwJBVV95cUxQU2MxX3J5UUpFa1RfaFFXUmhpT3UycXF4QnV3ZGF5UHRIYUVzUjRYUUZ1YVBjLUpULWhidkplTG5RTmZ0anpqN3RIdW1qNXNpTWNYUkxXT0xEYzI1Vkdjem1iQ2QwN3dDUG9kOFlyVTNxSkJUekN2MkxucHpFc01YUVpsYnFwNEIxRV83cE1UNHB6cGFkU0M3dmZZd3N3U0U0WjA0YXp2WWItWTRrUnFjZHhRd2FoNC15YjRWSE5QVFdfUDYxRy1OcEptNGhHelJMUThOUmpjQzVKQzlCNHhjbWVCVUlzWDk1VG03RjFRLVJtMzVrUFowdFJCcEx1T253SjRPLW4wLVNEMFVxdmR5N2Vjaw?oc=5",
      "https://news.google.com/rss/articles/CBMiwwFBVV95cUxPb0t1cGV5OS1FMTMwZlF2Y3VvdnZILUg2b2ZsRDV3Mzk2WkNLaDR4V3dEdXhSVS04YThNZWNyWEZzRzZIV2c1N0t4UmJhNEkzN1VrOVlQTVFWRlREczJyLXZmX05BdUlFWTUxWk9rbGxkNXVYRGlLZkxDLVdTZE9haEh6ZmRHdzhseDJ0SUNjclAyNElOdEM1dWVDa1BXb2ttR3pxSjJzQzVqdTluR2pLS2JFZU1fdnhqSlhBdWQxbWZNN2s?oc=5",
      "https://news.google.com/rss/articles/CBMijwFBVV95cUxQQTdsMGtfV1hncUFaM2F5X2hiNkd1SlJSZU5MTkRxMVBBakRLUlcwUkV3SDdFWlZzZTB2bTUwaEdtRTFKT0FpU19KYTNuZ1FveGdLV3Fsa29KUDZSdGtnSVgyLWZ3Nk1YNEEzU29yZ01jS01VX09rRDQtYU82NDc3UjBJTDZUVzU5QzJ4S2RrYw?oc=5"
    ]
  },
  {
    "topic_id": "09b10dce-6fe2-40a0-bce6-b4f3c335748e",
    "title": "Infosys shares get multiple downgrades, price target cuts after Q1 results; Deta",
    "category": "markets-finance",
    "coverage": "update",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMi-gJBVV95cUxOQjRvaGJkdnZRaWc2XzBReDB0ZHc4TjRSTENpWmtLMkpTcDRRckVlMlFXOWhDUWdqaUlwQjM5c0RRNXBzeHRJV3pWQUJIaW9xZzl6b20xSDJENU8zckhvWHN1SlRIeUtIYXRqVHBsY09MZGYzeV9SbEdGNUxfb2dFQ29CZmxNaVRPUFJFNDE1UDRrNFhTdlBxRXI2czI4RVR3V3gzcUNpUVk1QnhuS0ZiR09QMFplelFDNGd5TG4yV2FaM2xzejdsSnJHOHE2Z0gtYWg3c0R1bFdtQmVOTlNaaS1tYjgwQWpnX0RkZHJ5VjVZYUpJR0hIWmkxYUprU3RCSXRVQ2dfTGJZN1dfV0hWaEkwdlpJcGNJYjlDNEVISHZ0a1Y1bmwyNFhFeFRDS3FzajY3eXp6RUFyR2ZIYnJiTkllQUJSWll1OExNOGpDdmlhSVFNMEl6ZGw4aEJ0UmxBVGc0MVVQR2dQTTE0MGZfRHljWnU5dDd5bmfSAYADQVVfeXFMTV90aVdTMnBsSGYzVUxlR05jVmtLejVKRjZzSW5xUUZNWHNJbnpNNDl0Y3QzSEtqY0ViQ3U1SHpfR096X1NGNG9xcm1QcU9JckV1b0dDR1EtcXFNV1JlRXlBQXRISGFWcWNneXZMNlJnWTd0UjlNYms0LU84bUdwZ0xFR21xdzhvaHBFOG9OS2dabUlScEo5VEFNdVNWMTFjaE1jd3d6X1E4Tno0Yzl4VGlKWjM1OUVYcDR6NnhHRlVuTW1xdVhoMkQyZEZVWHFXdkhWTTBFR0g1WGhyblU2b2s0WmgwZDZ6V0xra2VKdG1ubFVtU2UtdDRLQThzR0xjdUlQODNzSjZna21XMTdNV2dCUHBiV3J4TGZkM291TWtiVW5Ic01VVXMtR1dSWFJvNEFLaUZLSEMyOHFrRjMtTkNOMDZGcmhNMFZGVEsteC11MGd6blgzcUMwS0tncDRraHgtV0wxY0lEbURSX1lCdmEwNFp1dUwxT2JEOWh6Z1VS?oc=5"
    ]
  },
  {
    "topic_id": "c1eede20-8c4c-434e-a66b-ed530926a91c",
    "title": "FDA says it identified new cyclospora outbreak linked to unspecified product - C",
    "category": "lifestyle-health",
    "coverage": "new",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMi0AFBVV95cUxPNXEwWHV4REdJdVQ2YUZ4SldaeC1QdzlRTktHRTJKY2R4NExfQ1M2ZzNTVDM2ZWlldXMyY2dEU0pCd2hZQU9qd3ZyOThvbFpFQnRFR0J6cjlNOXdDTldXNmhpWjBsTi1GRk91cWRndS14TUtBclJKOGw1dVBRei0tZVdQSFVxRlNYUVhGUnI5c2Y3eEVaazUtV1o5bWY3Sl92dUVoMm50Sms1VmNqbE1BYUZFWERqVVdkeGJVbkpwdnJaQzhaQ0ptVXQtSk5pUWZs?oc=5"
    ]
  },
  {
    "topic_id": "dd658eb5-f2f6-4974-8466-c551add6b3c6",
    "title": "What experts are saying as Ebola outbreak in Congo and Uganda kills more than 1,",
    "category": "news",
    "coverage": "new",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMitAFBVV95cUxQVFdpbnhRNGRZcTFJSnlNTFJFOFdDcmtGNkRCY1EtTUljRU8wVjVXRW9lNndwSTVEbUl4MHJHV0FObllHSzI4aDdtLVQybk9ScjlkQVhjX3IzTTFyNUFkR2psdmJPeXVERnRBY1VCYWltbXlxOWxiZUxYRlRxMXNaUkE0UnQyMHZfS0NBMDFGcWRzd2JVT1RVMFY1ekYxNUY0bkFtaU9ibkFoLUpQRWhGY0U4VUbSAboBQVVfeXFMT1RVUjNmdWphSkRKN2Z3QjBEZHZrN2VNOWo2RFh2T29EMTZVeXNpZjBRU2xvb01sYUU4Mm4wMU1uYnBWVDAyM2huSTdYVTVWYlJnekp6UXJtS212MG9xdDJCaG9OczdybkpSc3lFMV9fV3NfRFdhWmNrWl81NFRfQmU4d3JUSlN3X2RIUklDcDE1OFZmTzM3MEVwQTc4d21JR1RkLTgtU25nS1JpNUtDSmlsdEExeUVvcUJB?oc=5"
    ]
  },
  {
    "topic_id": "603c27a2-d120-4684-86f7-71a3334e40e1",
    "title": "Johnny Depp Makes Surprise Comic-Con Appearance as Ebenezer Scrooge - Variety",
    "category": "entertainment",
    "coverage": "new",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMivAFBVV95cUxQZTJTS3BQTFVlTGxMZ2dlYW9CVjB4akFyS0VaWGR3Q2FIV3dTSjAtRWZVLTR5YUI4VHV5czdIWWdqTDhWR3pqU3JObWhTRmpqTkJ5UHRmQ05sQ1VWbVlYUlJlLU81amwyendJOHh1VlhvcENUYlBVMVNzd0RYVmo0OEVHTW5GQWRYMkh6WnJQZU9GamdxM01jbzRjX0hIWVhTZEh4VERPTjFWUG9CdHRYY3ctdml3TG1aeFdmSA?oc=5",
      "https://news.google.com/rss/articles/CBMioAFBVV95cUxPbGtLam1NUERPcFluNGdDdFFwcU92MEsxa081VGVfUDVEaGdRS2QtdTNjQlpLT19sWnlCZnU2Qk5RWURiNzk0TUVUZ2FrWXAyQXJwX2JHS3FjN1hNYkFyaXJFTTgyNFlqLWVUaEZNRTRsbzE5alZLRkVhQXN6MzJ2cGFWa0NqX1RRS1hXbkdfd0tXZzBGRTNfM0ZFVnQ5MU9s?oc=5"
    ]
  },
  {
    "topic_id": "faeec7a4-c01d-4785-bb1c-5e7396eae132",
    "title": "Intel sales, profit forecast beat estimates; company boosts spending plans on AI",
    "category": "technology",
    "coverage": "new",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMif0FVX3lxTE1aVWlROTJqU3UxZUtSMzIycmZHRzloRFFtQTY2NjduVGhGekVlWEV5VUpLZ0dibzdUek5LQlEzLVRuUjlxTVYzNkFDY3RUMmYtczJQSGYtMEdqOWZqZW5KZUlGc2ZqZ2NubVUzSEU2VkFtUDhnV3dfYVQ1Y0hlaUU?oc=5"
    ]
  },
  {
    "topic_id": "679ef577-5e0f-4c74-b61e-f39129015b13",
    "title": "IBM CEO addresses Wall Street tech panic after delayed enterprise software deals",
    "category": "technology",
    "coverage": "new",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMikAFBVV95cUxQSHJCcVlfa3VRU29Cb2RFMmc1eXAzTFVsbFR4OEZjQk1BSkRWN2Z3cGdLZ2pranVVNDJwWFJFRjB0UGMzT0ZKejBLY0NMNWpiVlFLM2pHc0I0MHd6cG14QlNKVVhFeU9BS0NLUFZ5ejJOUlpYdkVjYldNdmxySFU1NnFlUEs1Zk9JLWUwblJ5VHE?oc=5"
    ]
  },
  {
    "topic_id": "babaf38f-2b75-4d14-9081-a4864bd55a85",
    "title": "Bangladesh PM Tarique Rahman invited to BRICS summit in Delhi - The Hindu",
    "category": "nri-world",
    "coverage": "new",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMitgFBVV95cUxNbnFYUXVYT1ZKR2Z0dUZqdU1fSkJOS2t5bW1URzlaUmtETW5fenFWSXhIdFUyX29BUy1TREVKNmw3Ujd1cExxTGxQckhGMHBGZXJjbWk4WWRHd2hEUGEtWjI4dlFiWjFYc1BlYzNlVXJZakFaSzlrcEJlSkFhcW5RRkFMb0hSS2tXSHlKTlNPRDMtSTdocUhmTEhFRWJ6V2cwYUVRODFWbE00OG9KNGFSWDI5WllGUdIBxgFBVV95cUxOTG9yT1hFdjJJUEowc2pnekczcFFISVZLZ1RndXI3QU16SlA4RUhERWhLVTRld1Z5NXFjbS1NYlVNeXhpeDdSd3oyWUUwcGdORS1FXzNLNkxMbWRWTUlMcDNCWENlV3lvaGNLcGd6ajVtdFRkYTdKaGlTbjEyamZpRHl4Y2VlZVpxWENQazhkbTNqclE0QkM0dW4xaThfVklVTlRzcTZ0dXh2ZWQ4OHB5Sk9Wd0NOVm5IYTBSbEdheDhPelM2d3c?oc=5",
      "https://news.google.com/rss/articles/CBMiyAFBVV95cUxOSWNvc2JVdTNTenFOcEZ1d0pBOUEwVGZHNjFSeHNtMWxfY1N3dmF5V1AwTkh6TS1pdkYyWmE2VHVXQ2tZR1NleEpoMWY1VWoxV1VlOUNIdlVTMU1iNVRtX21zUVh3UDkzZWZhZHpyTGpMOGJzZDdGenV5NjlJZ29qVmF5dDU2M1FJQ1VhZGgzUUJnRW5CQWhWV2JrQmc3V05VOThmTllTQUZTakE2OXF3VVFLem1WckI2UjhKR2h1UHl2V0VIN2pYRA?oc=5",
      "https://news.google.com/rss/articles/CBMi1AFBVV95cUxPSUpVNWNwbWJqWGpCMXdqUEljTmp4cjBEc1BNQXRETzNEWkJ5UXE4anN5MkNtMklqamFtcTlSdlBrMlJYMVlUZ1BmV0t2ZlBsM0FfbTNHMndsc0ZmN3h1WFZhQXE2eTFqWFhpLUNSRVA4RExfQnNFaDZCd202Nk1PRGFTUkY2MFl0eXZzR2lDQ0lvcnY0NU8tSUtwSTlMNVlRaDl5eGR2NVc2WDA4ck0wM2dGeVV5RldaTm9ycGI3WW5vLUwtcUNUSnBBWllieUpCVndxRA?oc=5"
    ]
  },
  {
    "topic_id": "489b6496-bcc2-49cc-8be3-d46462ee11bf",
    "title": "Simple Diet Change has the \u2018Superpower\u2019 to Lower LDL Cholesterol Naturally, Doct",
    "category": "lifestyle-health",
    "coverage": "new",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMihgFBVV95cUxNRXdERG5FTVBSejU1cm5UMEdxb05Kd21rSVpvZ1luQkV0QTRwcllrUDhxejVwb0xBNEpBQUZfOTJzVFhJOTUtZ1lvaXZuMlNxUFZCdmdLamprYmU1SW5FWUZZZTZ1SUhMN2VNT2lsbEp5YjRJb08xYVZJb1hqT1huaE1raVpnZw?oc=5"
    ]
  },
  {
    "topic_id": "088bc59c-e23d-432f-b007-9b36a01bd754",
    "title": "New Zealand Hotels Book Out Ahead of First Total Solar Eclipse In More Than 850 ",
    "category": "travel",
    "coverage": "new",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMiuwFBVV95cUxQSGg4cW1hZy1BcWpFT1E5WmszTDFEYlVNMHNHRTBOWE9tWUFCVmxMZzhmSWIxYzlyYlFNLVQ3MXEzWmwzaExvbzUzeWlORkdtU2VHYmxRRGRtOGZWQk43U2N0bnlXTnY1UDhKTDVJSkw3c1hXX1ZHQXFfWXpfUTE1WGJBeGdSdEpQS2xmemhjdDJicXFsaGZzZlpDS2IyeGVkdkY0aFR5RlJUUzQ5YWQ2cGhPZmQ3RTVacFVZ?oc=5"
    ]
  },
  {
    "topic_id": "f11f08c6-0152-4f5e-9ab7-bd231f85bb56",
    "title": "Canada boosts transparency on permanent resident admissions - CIC News",
    "category": "immigration",
    "coverage": "update",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMipwFBVV95cUxON1BUSUo1WnI0T3FWbUd6NFQyMzBBbGZOZlAzYXpoX2ZlZl9RbkY0QmRmQ3U5SDFlbEIzYUJlT200QWJvbUxLeTBWNnhhX3NpeXRZSmZJbERZSFEtT2V2T2pTcFhWdlJydFoxWW9GNXBDRTN3N0VCalVGNEhfOUI2U1JHRm52Nmp0aXkyX0VhaUM3c1RwRGJhMEFYU2hXU0VMTjF1allmQdIBjAJBVV95cUxQa2l1aWpVbkpjZkpNTnpnX04zUjZjZm9KSjJfVnFPS1ZodWVZdUxsbFV4TmJ3SVlaNUMwS0JFUDZINU5KR0NBLTMtQ2dmYjZ4cFNXbG9Cd0haVDd6bE42VTFSeTNPdDNCcldaUGpmRy1iRHJuRmFrVmtUSmNEUEdsUUNzQnFvYWhOS2JhdWN1T2tBNmJ2dmYyMi1tME5Sc1d1eGFXeW1kcnpXLTJIZkpUckg5TDktQ2ktVWx6Mk1pWmRwY1FPMmt3UlVTS21pUEY5RVBHc0ZMZmN6Nm9XUXhmU1dLeTc0QlVGcks3SUtCY0paMXdnZ3pYU2FYeW9lZVNVd2tTYmJhbnY0LV9Y?oc=5"
    ]
  },
  {
    "topic_id": "d0315bbd-90da-4a29-bf56-670d21e63079",
    "title": "Trump's $100,000 H-1B visa fee is unlawful, Federal judge rules - The Detroit Ne",
    "category": "immigration",
    "coverage": "update",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMitAFBVV95cUxQUkJOaHljdFZneEg5RjZCcEJFSVhfUzl4akROSEJzR19FLXc0Wi16OHJOMXROTGFtblVyZXdIb0xsZmExb2szekpvbGNvN2NHNms5d2xaaU5LYWx3c3ViRTJpSTZ4dG1ublNyWGNYUDdrOXBSRjlwMjBlb3paYmtlNHBsUy0xQWNYUDJILTM1ZEo5dkNvd2s5U0FmQnh2WHdJODJMT1cyY2RIazRNUkFXYmFUNFM?oc=5"
    ]
  },
  {
    "topic_id": "bb08bf3f-6a7d-4150-8e24-4158f473f300",
    "title": "Air India upgrades Delhi\u2013Toronto flights with new Boeing 787-9, removes Vienna f",
    "category": "travel",
    "coverage": "new",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMigwFBVV95cUxOYnpnU01oX1d0VmJ5S3lOY0g4bzMzS0xIMUxGSk1RU2JzTEJ4eEViMW1VWTVsTi1TLWhJNW9ZeG5pUTh0ZXRvUXdiU2kteUlIMXRoYUxFYWV6NzFoMFg0RERlQ2p3SGhHTjNDcTNQcGRVWnFBVjlmOEhWSm1veERmNnVyYw?oc=5",
      "https://news.google.com/rss/articles/CBMi6wFBVV95cUxOaGpLQXJ6dTJ6b0lMbzdNTXlIWDVTN2w3NW5IcTFUV2JqdHpUaGI1c1UxQnprLUZPOU92NkxNMng3UkR6dnpYMGFpRnJ6VDI1UDg2WXlQVmRmekZ5dXBfdWYtTlZNejd4T1VyYXh5U3VvLUFaOXpFejhrWmhGbFoweUZFWm9kdVNucnVfakZuaHlBcmh1SmMxbFFiR3RkVjYydl92V0NUVnJWalA3alk5bFdLcmMwQlFhOU00alMzbm91TmpaRmtSMGFvS3l6VkxjT01YcmpzcjU0VGV5RElKVXhnekEyZXlOQ2R3?oc=5"
    ]
  },
  {
    "topic_id": "c4970fe7-2bc6-47d3-8bb3-8c662f0e0ed5",
    "title": "Flipkart to launch food delivery over the coming weeks: Group CEO Kalyan Krishna",
    "category": "food",
    "coverage": "new",
    "source_urls": [
      "https://news.google.com/rss/articles/CBMi2wFBVV95cUxOZE05WVZfNUJNT3BXTk9zV3lzYUEwcktCR2tLbXlKajNLZFdQcWo0UXVDYnBrRG5Famo2U2hUZTQxUW9nX09lMnktUXhmS2VCdE10eVJtakd1T2hEYWotYzRHRXhDWk5HcEJUMHR3ejA0V0N5Xzl2QlNhcGVXb3NKR1lNWU94RThnWDd1Wjc5bTBJOEhIMF9PVmt1ZkdkWEZIY0NBRk0xY3NNZnFmMWVvamtCdl9WMDNJN3h0WjN1T0xGZDdIZEVMSUdiY2RTdG1OLXA3ZF85UC1ENEU?oc=5",
      "https://news.google.com/rss/articles/CBMivgFBVV95cUxNbjVQY0Q0RHR5WGo5VzVhRG1odFdxSHpWNlBqX2s0eDVQZ2dDamRlZkdNUEdIVW0ydWhEOTdmbG9YX3hpeG9YT19kOVRseDR3R1ZvaHJqalIwMWh3TUdyYmlzdHAtcjdmREluOWFwdGJuS2cySVIwYnNCX1Y2TDQtR3lMcGp3ZG8zd3JvWnZZR0VGcmRmbUpRYjQzY25oZVRsTVROQXBwNXRiVEZWTmJTYWcyVmNjTzZkNDJhdzV30gHGAUFVX3lxTFBONjIzckxoS1RWTlB2OGxObTNZY01aTzFndU94dVVRLXExb19GcHVOMVFTRzZUbnNkNndiaVQzLU9aU0doWVh3T1ZaS1BEZEE4RDlYU3V1UTc4VVp1Y05PTnZieFEtY29TamI1VVIxQl9GRTgyWEV1OWU5Q0RuZFMzX2lFQ3hIRHpOcjRBTGN5X3FsR2FPRzl5SzJiR19HaUxweGtyQTlkZUExVkc3dVBhakNaRTFoeGx4aFNKNHRQQTBvU3JIZw?oc=5",
      "https://news.google.com/rss/articles/CBMi3wFBVV95cUxNZ2FnLXo5dEJjT1p2VHliRGpUTnRyZG1zUGdCVDR5aGlWZHROV2VoR2Z4N0NJME5ZcnRrbmJpa2hsMHhxbE1ZWXhITXpHQWlmTGFxYUdtc2RBcHJjOFJxNXV3NE5CRnZ1UE81dmVtUm1femNXV00zcmxRSVpvS2hsLUZPTkVBME5DQXB6a2swb3NkQm9JRXdzWkNpZ1FDWmRsYlhHLTNSbXhFM1lOSTZubEZObXdZaHFfSGljMXNjZTQ2X3cxa0h6bDhUZW5LcXh6WU5Wd1VheHp6ancyT2FN?oc=5"
    ]
  }
];

log("Processing " + candidates.length + " candidates");

phase("write-articles");

const buildPrompt = (c) => {
  const mergeNote = c.merge_topic_ids
    ? "\nMERGED TOPICS - update BOTH topic IDs after insert: " + JSON.stringify(c.merge_topic_ids)
    : "";
  const updateNote = c.coverage === "update"
    ? "\nThis is an UPDATE to prior coverage. Frame as a new development."
    : "";

  return "Write and publish ONE article for The Videshi (Indian diaspora news site).\n\n" +
    "Read ~/workspace/the-videshi-news/pipeline/V3-WRITER-INSTRUCTIONS.md section 3c for format rules.\n\n" +
    "CANDIDATE:\n" +
    "Topic ID: " + c.topic_id + "\n" +
    "Title: " + c.title + "\n" +
    "Category: " + c.category + "\n" +
    "Sources: " + JSON.stringify(c.source_urls) +
    mergeNote + updateNote + "\n\n" +
    "STEPS:\n" +
    "1. RESEARCH: browser_open 2-3 source URLs (Google News RSS redirects). If they fail, browser_search the topic.\n\n" +
    "2. WRITE (500-800 words HTML):\n" +
    "   - Headline: 8-14 words, clear, active\n" +
    "   - Subheadline: 1-2 sentences\n" +
    '   - Key takeaways: <div class=\"key-takeaways\"><ul><li>...</li></ul></div> (NO heading inside)\n' +
    "   - Body HTML with <h2> subheadings: lead, context, impact, diaspora angle, outlook\n" +
    '   - Pull quotes if strong: <blockquote class=\"pull-quote\"><p>\"...\"</p><cite>\\u2014 Name, Title</cite></blockquote>\n' +
    "   - NO filler phrases. Cite sources naturally. Use specific facts only from sources.\n\n" +
    "3. SLUG: from headline, lowercase hyphens, max 80 chars\n\n" +
    "4. INSERT: Write Python script to /tmp/insert-" + c.topic_id.substring(0, 8) + ".py:\n" +
    "   - Build JSON: headline, subheadline, body, slug, category='" + c.category + "', vertical='" + c.category + "',\n" +
    "     tags (array), sources (array), image_url=null, image_caption=null, image_attribution=null,\n" +
    "     word_count, diaspora_angle (string), topic_id='" + c.topic_id + "', llm_score=5,\n" +
    "     published_at (ISO now), article_type='breaking', status='published'\n" +
    "   - POST via subprocess curl to $SUPABASE_URL/rest/v1/p2_articles\n" +
    "     Headers: apikey + Authorization Bearer + Content-Type + Prefer return=representation\n" +
    "   - Print article ID\n" +
    "   Run: " + ENV + " && python3 -u /tmp/insert-" + c.topic_id.substring(0, 8) + ".py\n\n" +
    "5. IMAGE: " + ENV + " && cd ~/workspace/the-videshi-news/pipeline && python3 -u image_sourcer.py --slug SLUG --apply\n\n" +
    "6. UPDATE TOPIC: curl PATCH p2_topics id=eq." + c.topic_id + " with status=published, last_article_id=ID\n" +
    (c.merge_topic_ids ? "   Also PATCH topic " + c.merge_topic_ids[1] + "\n" : "") +
    "\nReturn: headline, slug, category, article_id, status (published/failed)";
};

const results = await parallel(
  candidates.map((c, i) => {
    return async () => {
      const r = await agent(buildPrompt(c), {
        key: "art-" + i + "-" + c.category.replace(/[^a-z]/g, ""),
        label: c.title.substring(0, 50),
        timeoutMs: 600000,
        schema: {
          type: "object",
          properties: {
            headline: { type: "string" },
            slug: { type: "string" },
            category: { type: "string" },
            article_id: { type: "string" },
            status: { type: "string" }
          },
          required: ["headline", "category", "status"]
        }
      });
      log("Done " + i + " [" + c.category + "]: " + (r ? r.headline : "FAIL"));
      return r;
    };
  }),
  { concurrency: 4 }
);

const ok = results.filter(function(r) { return r && r.status === "published"; });
const fail = results.filter(function(r) { return !r || r.status === "failed"; });
log("Articles: " + ok.length + " published, " + fail.length + " failed");

phase("post-processing");

const enr = await agent(
  "Run post-publish enrichment for The Videshi using exec commands:\n" +
  "set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.google-ai; " +
  "source ~/workspace/.env.pexels 2>/dev/null; source ~/workspace/.env.twitterapi-io 2>/dev/null; " +
  "source ~/workspace/.env.apify 2>/dev/null; source ~/workspace/.env.youtube 2>/dev/null; set +a\n" +
  "cd ~/workspace/the-videshi-news/pipeline\n" +
  "timeout 180 python3 -u enrich-on-publish.py --hours 3 --apply\n" +
  "timeout 600 python3 -u enrich-articles.py --hours 3 --apply\n" +
  "timeout 600 python3 -u enrich-data-cards.py --since-hours 3 --limit 10\n" +
  "python3 -u image_sourcer.py --backfill --hours 3 --apply\n" +
  "timeout 120 python3 -u proofread-article.py --hours 3 --apply\n" +
  "python3 -u prebuild-feeds.py\n" +
  "cd ~/workspace/the-videshi-news && git add -A && git commit -m 'V3 pipeline 2026-07-24' && git push origin main\n" +
  "Report what each step did.",
  { key: "enrich", label: "Enrichment + feeds + git", timeoutMs: 900000,
    schema: { type: "object", properties: { summary: { type: "string" } }, required: ["summary"] } }
);

const headlines = ok.map(function(a) { return "[" + a.category + "] " + a.headline; });
return "Published " + ok.length + "/" + candidates.length + " articles.\n" +
  headlines.map(function(h) { return "- " + h; }).join("\n") +
  "\nEnrichment: " + (enr ? enr.summary : "done");
