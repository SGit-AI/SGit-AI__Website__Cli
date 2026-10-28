# The brief for cli.sgit.ai, 20 October 2026, cli.sgit.ai

> The voice brief that started this site, published in full as transcribed, with the request that came with it: make cli.sgit.ai the CLI's main documentation, move the most technical content here from sgit.ai, and publish the CLI team's research as articles.

*Source: <https://cli.sgit.ai/briefs/2026-10-20__cli-sgit-ai-first-brief.html> · generated from the same content as the page, so the two cannot drift.*

---
# The brief for cli.sgit.ai, 20 October 2026

**Status:** accepted; the first version of this site (v0.1.0) was built from it the same day. **Written by:** Dinis Cruz, spoken, transcribed by Otter.ai. **Published:** in full and as transcribed, including the transcription's errors. What the errors stand for, and anything the build found the brief to be wrong about, is in [the corrections file](../admin/corrections.md), not here.

## The brief, as transcribed

> Okay, so this is now a brief for the the agent that is going to build the API website for the CLI, which is going to be at cli.sketo.ai, and the idea is to start to make this the main documentation repo for the CLI. At the moment, we're kind of using Escrip. AI, but I think we need to start moving some of that content here, or at least the most technical and the most detailed and stuff like that, and also to provide a way for the creation of specific articles that top that focus on specific topics and specific sort of implementations or specific ideas, which is something that we've talked before and we have we start doing in other websites, which is basically the place where we start to capture it first is almost like our new generation of briefs, which work better here, right? So then that's a lovely place to put that stuff. So I think to start with, let's just move the content because the CLI now starts to have a whole set of use cases that are even independent, and the Skit is more of the commercialization, the over umbrella, because we now have a lot of excrete usages, usages, right? So we can refactor it like that.

*Transcribed by https://otter.ai*

## The request that came with it (the initial prompt)

> Hi can you take a look at this brief and create the first version of this website.
>
> Also, take a look at a lot of the content in sk.ai that we can move, and also look at the content that is already on the main repo for the CLI, which that has been having a bunch of articles published that we should now also publish here as articles as the latest research capabilities, sorry, research topics.
>
> please push to dev once you completed the first setup
>
> see guidance at sgit.ai for how to setup these websites

## What the brief asks for, read plainly

1. **cli.sgit.ai becomes the main documentation for the sgit CLI.** sgit.ai stays the umbrella: the project, the vault platform, the commercial side.
2. **Move the most technical and detailed content here from sgit.ai.** The CLI now has use cases of its own, independent of the rest of the project.
3. **A place for articles that each take one topic, one implementation or one idea as far as it goes.** These are "our new generation of briefs", and they are captured here first.
4. **Publish the research the CLI repository already holds** as those articles.
5. **Follow the estate's guidance for setting up a site**, and push the first version to `dev`.

## How the first version answers it

| Ask | Where it is |
|---|---|
| 1. The CLI's main documentation | [the docs](../docs/index.md) and [the command reference](../reference/index.md), every command generated from the CLI's own parser |
| 2. Move the technical content | 190 pages in all; the ones that moved, with where each was: [What moved from sgit.ai](../admin/moved.md) |
| 3. A place for topic articles | [Articles](../articles/index.md), in the newsroom's format since v0.2.0; publishing one is adding one file, the contract is in `admin/content/articles/README.md` |
| 4. The CLI repository's research | [Research](../research/index.md): 60 documents in 8 topics since v0.2.0, each with its source path and commit; in v0.1 they were under Articles |
| 5. The estate's guidance | [Every sgit repository](https://sgit.ai/docs/guidance/repositories.html), followed item by item on [the engineering page](../admin/index.md), with what is not done yet in [the reality file](../admin/reality.md) |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/briefs/2026-10-20__cli-sgit-ai-first-brief.html)*
