<template id="page-orangepillmerchants">
  <div class="row q-col-gutter-md">
    <div class="col-12">
      <q-card>
        <q-card-section class="row items-center q-col-gutter-md">
          <div class="col">
            <div class="text-h5">Orange Pill Merchants</div>
            <div class="text-subtitle2 text-grey-7">
              Create merchant onboarding records, issue the public TPoS link, and automatically
              release account access once the onboarding amount has been repaid.
            </div>
          </div>
          <div class="col-auto">
            <q-btn color="primary" unelevated @click="showCreateForm()">New merchant</q-btn>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <div class="col-12">
      <q-card>
        <q-card-section>
          <div class="row items-center q-col-gutter-md q-mb-md">
            <div class="col">
              <q-input v-model="merchantsTable.search" dense :label="$t('search')">
                <template v-slot:before>
                  <q-icon name="search"></q-icon>
                </template>
              </q-input>
            </div>
          </div>

          <q-table
            dense
            flat
            :rows="merchants"
            row-key="id"
            :columns="merchantsTable.columns"
            v-model:pagination="merchantsTable.pagination"
            :loading="merchantsTable.loading"
            @request="getMerchants"
          >
            <template v-slot:header="props">
              <q-tr :props="props">
                <q-th auto-width></q-th>
                <q-th v-for="col in props.cols" :key="col.name" :props="props">
                  ${ col.label }
                </q-th>
              </q-tr>
            </template>

            <template v-slot:body="props">
              <q-tr :props="props">
                <q-td auto-width>
                  <q-btn
                    flat
                    dense
                    size="xs"
                    icon="mail"
                    color="primary"
                    @click="resendMerchantEmail(props.row)"
                  >
                    <q-tooltip>Resend merchant email</q-tooltip>
                  </q-btn>
                  <q-btn
                    flat
                    dense
                    size="xs"
                    icon="delete"
                    color="negative"
                    @click="deleteMerchant(props.row.id)"
                  >
                    <q-tooltip>Delete onboarding record</q-tooltip>
                  </q-btn>
                </q-td>
                <q-td key="name" :props="props">${ props.row.name }</q-td>
                <q-td key="email" :props="props">${ props.row.email }</q-td>
                <q-td key="currency" :props="props">${ props.row.currency }</q-td>
                <q-td key="onboarding_amount" :props="props">
                  ${ props.row.onboarding_amount.toFixed(2) }
                </q-td>
                <q-td key="repaid_amount" :props="props">
                  ${ props.row.repaid_amount.toFixed(2) }
                </q-td>
                <q-td key="onboarding_completed" :props="props">
                  <q-badge :color="props.row.onboarding_completed ? 'positive' : 'orange'">
                    ${ props.row.onboarding_completed ? 'Yes' : 'No' }
                  </q-badge>
                </q-td>
                <q-td key="tpos_id" :props="props">
                  <a :href="tposUrl(props.row)" target="_blank">${ props.row.tpos_id }</a>
                </q-td>
                <q-td key="updated_at" :props="props">
                  ${ dateFromNow(props.row.updated_at) }
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </div>

    <q-dialog v-model="formDialog.show">
      <q-card style="width: 640px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">New merchant onboarding</div>
        </q-card-section>
        <q-card-section>
          <div class="q-gutter-md">
            <q-input
              v-model="formDialog.data.name"
              label="Merchant name"
              filled
            ></q-input>
            <q-input
              v-model="formDialog.data.email"
              label="Merchant email"
              filled
            ></q-input>
          </div>

          <div class="row q-col-gutter-md q-mt-sm">
            <div class="col-12 col-sm-6">
              <q-select
                v-model="formDialog.data.currency"
                :options="currencyOptions"
                label="Fiat currency"
                filled
              ></q-select>
            </div>
            <div class="col-12 col-sm-6">
              <q-input
                v-model.number="formDialog.data.onboarding_amount"
                type="number"
                step="0.01"
                min="0.01"
                label="Cash given"
                filled
              ></q-input>
            </div>
            <div class="col-12">
              <q-select
                v-model="formDialog.data.source_wallet_id"
                emit-value
                map-options
                :options="wallets.map(wallet => ({label: wallet.name, value: wallet.id}))"
                label="Recoup wallet"
                filled
              ></q-select>
            </div>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat v-close-popup>Cancel</q-btn>
          <q-btn color="primary" unelevated @click="saveMerchant()">Create</q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>
