import ChatTTS
import torch
import torchaudio
import torch._dynamo

torch._dynamo.config.suppress_errors = True

chat = ChatTTS.Chat()
chat.load(compile=True) # Set to True for better performance

texts = ["Stardust Dragon is a Level eight Synchro monster that acts as a safeguard against destruction. The moment an effect threatens to wipe out a card on the field, Stardust Dragon can Tribute itself to shut it down, negating the activation and destroying the source. But it doesn’t stay gone for long. if its effect goes through, it returns from the Graveyard at the end of the turn, ready to protect your field all over again. Reliable, reactive, and hard to keep down, Stardust Dragon is the definition of a defensive ace."]

wavs = chat.infer(texts)

for i in range(len(wavs)):
    """
    In some versions of torchaudio, the first line works but in other versions, so does the second line.
    """
    try:
        torchaudio.save(f"basic_output{i}.wav", torch.from_numpy(wavs[i]).unsqueeze(0), 24000)
    except:
        torchaudio.save(f"basic_output{i}.wav", torch.from_numpy(wavs[i]), 24000)