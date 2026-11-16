/* Ahmet Mete Kenru, 5001240001, G3 - v2 (4g: checksum kept in a local during pass 2) */
#define N 25

const int SID = 1240001;

int msg[N];
int orig[N];
unsigned int checksum;
int decrypt_ok;

unsigned int rotl(unsigned int x, int n)
{
    return (x << n) | (x >> (32 - n));
}

int main(void)
{
    unsigned int x = SID;
    int key = SID % 256;
    int i;
    unsigned int c;

    if (key == 0)
        key = 0xA5;

    /* pass 1: generate the message with the LCG */
    for (i = 0; i < N; i++) {
        x = 1664525u * x + 1013904223u;
        msg[i] = ((x >> 16) % 26) + 65;
        orig[i] = msg[i];
    }

    /* pass 2: encrypt in place and compute checksum */
    c = 0;
    for (i = 0; i < N; i++) {
        msg[i] = msg[i] ^ key;
        c = rotl(c, 1) + msg[i];
    }
    checksum = c;

    /* pass 3: decrypt and compare with the original */
    decrypt_ok = 1;
    for (i = 0; i < N; i++) {
        msg[i] = msg[i] ^ key;
        if (msg[i] != orig[i])
            decrypt_ok = 0;
    }

    return 0;
}
