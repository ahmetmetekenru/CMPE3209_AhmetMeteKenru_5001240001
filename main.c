/* Ahmet Mete Kenru, 5001240001, G3 */
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

    if (key == 0)
        key = 0xA5;

    /* pass 1: generate the message with the LCG */
    for (i = 0; i < N; i++) {
        x = 1664525u * x + 1013904223u;
        msg[i] = ((x >> 16) % 26) + 65;
        orig[i] = msg[i];
    }

    /* pass 2: encrypt in place and compute checksum */
    checksum = 0;
    for (i = 0; i < N; i++) {
        msg[i] = msg[i] ^ key;
        checksum = rotl(checksum, 1) + msg[i];
    }

    /* pass 3: decrypt and compare with the original */
    decrypt_ok = 1;
    for (i = 0; i < N; i++) {
        msg[i] = msg[i] ^ key;
        if (msg[i] != orig[i])
            decrypt_ok = 0;
    }

    return 0;
}
